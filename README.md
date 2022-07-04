# TimeClock

You can find the documentation of the GraphQL API's below:

https://documenter.getpostman.com/view/1603718/UzJFwz3C

# Dependencies
`Python >= 3.8`

`Django >= 3.1.4`

`Sqlite`

# Virtual Environment Setup
Setup virtualenv with command: 

`$ virtualenv -p python3.8 timeclock`

Move to virtualenv and activate its environment:

`$ cd timeclock`

`$ source bin/activate`


# Github Repository Setup
Go to the link: https://github.com/itsayushbansal/timeclock

Clone this new repository : 

`$ git clone https://github.com/itsayushbansal/timeclock.git`

Using Command Line, navigate to the repository

`$ cd timeclock`

# Dependency Setup
Install requirements: 

`$ pip install -r requirements.txt`

Run migrations: 

`$ python manage.py migrate`

Create superuser: 

`$ python manage.py createsuperuser`

# Run Application
`$ python manage.py runserver`
