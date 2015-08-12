__author__ = 'wilrona'

from lib.flaskext import wtf
from lib.flaskext.wtf import validators
from application import function
import datetime
from lib.pytz.gae import pytz

time_zones = pytz.timezone('Africa/Douala')
date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")


def departure_date_activate(form, field):
    date = function.date_convert(field.data)
    if datetime.date.today() > date:
        raise wtf.ValidationError('The departure date must be greater than or equal to the current date.')


def schedule_activate(form, field):
    time = function.time_convert(field.data)
    if function.date_convert(form.departure_date.data) == datetime.date.today():
        if function.datetime_convert(date_auto_nows).time() >= time:
            raise wtf.ValidationError('Time of departure of the current date must be greater than or equal to the current time.')



class FormDeparture(wtf.Form):
    departure_date = wtf.DateField(label='Departure Date', validators=[validators.Required(), departure_date_activate], format="%d/%m/%Y")
    schedule = wtf.StringField(label='Departure Time', validators=[validators.Required(), schedule_activate])
    destination = wtf.StringField(label='Select Travel line', validators=[validators.Required()])
    vessel = wtf.StringField(label='Select Vessel', validators=[validators.Required()])