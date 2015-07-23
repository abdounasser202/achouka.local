__author__ = 'wilrona'

from google.appengine.ext import ndb


class CustomerModel(ndb.Model):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    birthday = ndb.DateProperty()
    passport_number = ndb.StringProperty()
    nic_number = ndb.StringProperty()
    profession = ndb.StringProperty()
    nationality = ndb.StringProperty()
    phone = ndb.StringProperty()
    dial_code = ndb.StringProperty()
    email = ndb.StringProperty()
    is_new = ndb.BooleanProperty(default=True)
    status = ndb.BooleanProperty(default=True)
