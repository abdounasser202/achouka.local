__author__ = 'wilrona'


from lib.flaskext import wtf
from lib.flaskext.wtf import validators


class FormProfil(wtf.Form):
    name = wtf.StringField(label='Profile Name', validators=[validators.Required(), validators.length(max=50)])
    standard = wtf.IntegerField(label='Select Standard', default=2, validators=[validators.Required()])
    enable = wtf.BooleanField(default=True)