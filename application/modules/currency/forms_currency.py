__author__ = 'wilrona'


from lib.flaskext import wtf
from lib.flaskext.wtf import validators


class FormCurrency(wtf.Form):
    code = wtf.StringField(label='Code :',  validators=[validators.Required()])
    name = wtf.StringField(label='Name :',  validators=[validators.Required()])


class FormEquivalence(wtf.Form):
    value = wtf.IntegerField(label=' Value Rate ', validators=[validators.Required()])
    currencyEqui = wtf.StringField()