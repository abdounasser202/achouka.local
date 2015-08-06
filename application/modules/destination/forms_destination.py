__author__ = 'wilrona'

from lib.flaskext import wtf
from lib.flaskext.wtf import validators


class FormDestination(wtf.Form):
    code = wtf.StringField(label='Destination Code', validators=[validators.Required()])
    name = wtf.StringField(label='Destination Name', validators=[validators.Required()])
    currency = wtf.StringField(label='Select currency')