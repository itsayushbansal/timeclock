from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class CustomUser(AbstractUser):

    email = models.EmailField(blank=False, max_length=255, verbose_name='email')

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'


class Entries(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    start_time = models.DateTimeField(auto_now_add=True, null=False)
    end_time = models.DateTimeField(null=True)
    hours = models.IntegerField(null=True)
    date_dy = models.IntegerField(null=False)
    date_mo = models.IntegerField(null=False)
    date_yr = models.IntegerField(null=False)
    date_wk = models.IntegerField(null=False)

