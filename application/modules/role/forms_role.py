__author__ = 'wilrona'

from lib.flaskext import wtf
from lib.flaskext.wtf import validators


class FormRole(wtf.Form):
    name = wtf.StringField(label='Name role', validators=[validators.length(max=50), validators.Required()])
    visible = wtf.BooleanField(default=True)