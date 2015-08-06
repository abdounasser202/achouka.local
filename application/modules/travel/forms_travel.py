__author__ = 'wilrona'

from lib.flaskext import wtf
from lib.flaskext.wtf import validators

class FormTravel(wtf.Form):
    time = wtf.StringField(label='Line Travel Time')
    destination_start = wtf.StringField(label='Select departure', validators=[validators.Required()])
    destination_check = wtf.StringField(label='Select destination', validators=[validators.Required()])