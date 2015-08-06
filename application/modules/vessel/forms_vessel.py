__author__ = 'wilrona'


from lib.flaskext import wtf
from lib.flaskext.wtf import validators

class FormVessel(wtf.Form):
    name = wtf.StringField(label='Vessel Name :', validators=[validators.Required()])
    capacity = wtf.IntegerField(label='Capacity :', validators=[validators.Required(), validators.NumberRange(min=1, max=1000000)])
    immatricul = wtf.StringField(label='Immatriculation :')

    def validate_capacity(self, field):
        if field.data <=0 and field.data:
            raise validators.ValidationError('Capacity should be more than zero')

        if not isinstance(field.data, int) and field.data:
            raise validators.ValidationError('Enter capacity in figures')

