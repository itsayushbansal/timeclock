import datetime
from datetime import timezone
import graphene
from graphql_auth import mutations
from graphql_auth.schema import UserQuery, MeQuery
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.models import Sum

from .models import Entries


class EntriesType(DjangoObjectType):

    class Meta:
        model = Entries
        fields = ('id', 'start_time', 'end_time', 'hours', 'date_mo', 'date_wk', 'date_dy', 'date_yr')


class ClockedHoursType(graphene.ObjectType):

    today = graphene.Int()
    current_week = graphene.Int()
    current_month = graphene.Int()


class CustomRegister(mutations.Register):
    id = graphene.Int()
    username = graphene.String()
    email = graphene.String()

    @classmethod
    def resolve_mutation(cls, *args, **kwargs):
        res = super().resolve_mutation(*args, **kwargs)
        if not res.success:
            return res
        email = kwargs.get("email")
        user = get_user_model().objects.filter(email=email).first()
        res.__dict__.update({'id': user.pk if user else None,
                             'username': user.username if user else None,
                             'email': user.email if user else None})
        return res


class CustomObtainJSONWebToken(mutations.ObtainJSONWebToken):
    expires_in = graphene.Int()

    @classmethod
    def resolve_mutation(cls, *args, **kwargs):
        res = super().resolve_mutation(*args, **kwargs)
        if not res.success:
            return res
        res.__dict__['expires_in'] = settings.GRAPHQL_JWT['JWT_EXPIRATION_DELTA'].seconds
        return res


class ClockInMutation(graphene.Mutation):

    class Arguments:
        user = graphene.Int(required=True)

    clock_in = graphene.Field(EntriesType)

    @classmethod
    def mutate(cls, root, info, user):
        user_obj = info.context.user
        if not user_obj.is_authenticated:
            raise Exception('Unauthenticated Request')
        if user_obj.id != user:
            raise Exception('Invalid JWT Token')
        current_date = datetime.datetime.now(timezone.utc)
        obj = Entries.objects.filter(user_id=user, date_dy=current_date.day, date_mo=current_date.month,
                                     date_yr=current_date.year)
        if obj:
            raise Exception('Already Clocked In for today')
        clock_in = Entries(user_id=user, start_time=current_date, date_dy=current_date.day,
                           date_mo=current_date.month, date_yr=current_date.year, date_wk=current_date.isocalendar()[1])
        clock_in.save()
        return ClockInMutation(clock_in=clock_in)


class ClockOutMutation(graphene.Mutation):

    class Arguments:
        user = graphene.Int(required=True)

    clock_out = graphene.Field(EntriesType)

    @classmethod
    def mutate(cls, root, info, user):
        user_obj = info.context.user
        if not user_obj.is_authenticated:
            raise Exception('Unauthenticated Request')
        if user_obj.id != user:
            raise Exception('Invalid JWT Token')
        current_date = datetime.datetime.now(timezone.utc)
        obj = Entries.objects.filter(user_id=user, date_dy=current_date.day, date_mo=current_date.month,
                                     date_yr=current_date.year).first()
        if not obj:
            raise Exception("You've not yet clocked in for the day.")
        if obj.end_time is not None:
            raise Exception("Already Clocked Out for today")
        obj.end_time = datetime.datetime.now(timezone.utc)
        obj.hours = int((obj.end_time - obj.start_time).seconds // 3600)
        obj.save()
        return ClockOutMutation(clock_out=obj)


class AuthMutation(graphene.ObjectType):
    create_user = CustomRegister.Field()
    obtain_token = CustomObtainJSONWebToken.Field()
    clock_in = ClockInMutation.Field()
    clock_out = ClockOutMutation.Field()


class CurrentClock(graphene.ObjectType):
    current_clock = graphene.Field(EntriesType)

    def resolve_current_clock(root, info):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Unauthenticated Request')
        current_date = datetime.datetime.now(timezone.utc)
        obj = Entries.objects.filter(user_id=user.id, date_dy=current_date.day, date_mo=current_date.month,
                                     date_yr=current_date.year).first()
        if obj:
            return obj
        return None


class ClockedHours(graphene.ObjectType):
    clocked_hours = graphene.Field(ClockedHoursType)

    def resolve_clocked_hours(root, info):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Unauthenticated Request')
        current_date = datetime.datetime.now(timezone.utc)
        obj = Entries.objects.filter(user_id=user.id, date_dy=current_date.day, date_mo=current_date.month,
                                     date_yr=current_date.year).first()
        today = obj.hours if obj else None
        obj = Entries.objects.filter(user_id=user.id, date_mo=current_date.month, date_yr=current_date.year)\
                             .aggregate(Sum('hours'))
        current_month = obj['hours__sum'] if obj else None
        obj = Entries.objects.filter(user_id=user.id, date_wk=current_date.isocalendar()[1], date_yr=current_date.year)\
                             .aggregate(Sum('hours'))
        current_week = obj['hours__sum'] if obj else None
        return {'today': today, 'current_month': current_month, 'current_week': current_week}


class Query(UserQuery, MeQuery, CurrentClock, ClockedHours, graphene.ObjectType):
    pass


class Mutation(AuthMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
