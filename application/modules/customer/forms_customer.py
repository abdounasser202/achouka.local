__author__ = 'wilrona'

from lib.flaskext import wtf
from lib.flaskext.wtf import validators


def unique_email_validator(form, field):
    if not field.data:
        field.errors[:] = []
        raise validators.StopValidation()


def verify_dial_code(form, field):
    if form.phone.data:
        if not field.data:
            raise wtf.ValidationError('Select country code.')


def verify_format_number(form, field):
    if form.dial_code.data:
        # appel de la librairie de verification de numero de telephone
        from lib.python_phonenumbers.python import phonenumbers
        from lib.python_phonenumbers.python.phonenumbers import geocoder

        number = field.data
        code = form.dial_code.data

        phone_number = str(code)+str(number)
        numbers = phonenumbers.parse(phone_number, None)
        country_name = str(geocoder.description_for_number(numbers, "en"))
        if not country_name:
            raise wtf.ValidationError('Error! Your mobile number is not valid!')


def first_name_validator(form, field):
    """ Username must cont at least 3 alphanumeric characters long"""
    first_name = field.data
    if len(first_name) < 3:
        raise wtf.ValidationError('Username must be at least 3 characters long')
    valid_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._ '
    chars = list(first_name)
    for char in chars:
        if char not in valid_chars:
            raise wtf.ValidationError("Username may only contain letters, numbers, '-', '.' and '_'.")


def last_name_validator(form, field):
    """ Username must cont at least 3 alphanumeric characters long"""
    last_name = field.data
    if len(last_name) < 3:
        raise wtf.ValidationError('Username must be at least 3 characters long')
    valid_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._ '
    chars = list(last_name)
    for char in chars:
        if char not in valid_chars:
            raise wtf.ValidationError("Username may only contain letters, numbers, '-', '.' and '_'.")


def passport_number_validator(form, field):
    if not form.child.data:
        if not field.data and not form.nic_number.data:
            raise wtf.ValidationError("Field required")


def nic_number_validator(form, field):
    if not form.child.data:
        if not field.data and not form.passport_number.data:
            raise wtf.ValidationError("Field required")


class FormCustomer(wtf.Form):
    first_name = wtf.StringField(label='First name', validators=[validators.Required(), first_name_validator])
    last_name = wtf.StringField(label='Last name', validators=[validators.Required(), last_name_validator])
    birthday = wtf.DateField(label='Birthday', validators=[validators.Required()], format="%d/%m/%Y")
    passport_number = wtf.StringField(label="Passport number", validators=[passport_number_validator])
    nic_number = wtf.StringField(label="NIC number", validators=[nic_number_validator])
    profession = wtf.StringField(label='Occupation')
    nationality = wtf.StringField(label='Nationality', validators=[validators.Required()])
    email = wtf.StringField(label='Email', validators=[unique_email_validator, validators.Email()])
    dial_code = wtf.StringField(label='Country code', validators=[verify_dial_code])
    phone = wtf.StringField(label='Mobile Phone Number', validators=[verify_format_number])
    child = wtf.HiddenField()


class FormCustomerSearch(wtf.Form):
    first_name = wtf.StringField(label='First name', validators=[validators.Required(), first_name_validator])
    last_name = wtf.StringField(label='Last name', validators=[validators.Required()])
    birthday = wtf.DateField(label='Birthday', validators=[validators.Required()], format="%d/%m/%Y")


class FormCustomerPOS(wtf.Form):
    first_name = wtf.StringField(label='First name', validators=[validators.Required(), first_name_validator])
    last_name = wtf.StringField(label='Last name', validators=[validators.Required(), last_name_validator])
    birthday = wtf.DateField(label='Birthday', validators=[validators.Required()], format="%d/%m/%Y")
    passport_number = wtf.StringField(label="Passport number", validators=[passport_number_validator])
    nic_number = wtf.StringField(label="NIC number", validators=[nic_number_validator])
    profession = wtf.StringField(label='Occupation')
    nationality = wtf.StringField(label='Nationality', validators=[validators.Required()])
    email = wtf.StringField(label='Email', validators=[unique_email_validator, validators.Email()])
    phone = wtf.StringField(label='Mobile Phone Number', validators=[verify_format_number])
    dial_code = wtf.StringField(label='Country code', validators=[verify_dial_code])
    type_name = wtf.StringField(validators=[validators.Required()])
    class_name = wtf.StringField(validators=[validators.Required()])
    journey_name = wtf.StringField(validators=[validators.Required()])
    current_departure = wtf.HiddenField()
    child = wtf.HiddenField()
