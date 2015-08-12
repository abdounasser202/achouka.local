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
    date_update = ndb.DateProperty(auto_now=True)

    def make_to_dict(self):
        to_dict = {}
        to_dict['customer_id'] = self.key.id()
        to_dict['customer_first_name'] = self.first_name
        to_dict['customer_last_name'] = self.last_name
        to_dict['customer_birthday'] = str(self.birthday)
        to_dict['customer_passport_number'] = self.passport_number
        to_dict['customer_nic_number'] = self.nic_number
        to_dict['customer_profession'] = self.profession
        to_dict['customer_nationality'] = self.nationality
        to_dict['customer_phone'] = self.phone
        to_dict['customer_dial_code'] = self.dial_code
        to_dict['customer_email'] = self.email
        to_dict['customer_is_new'] = self.is_new
        to_dict['customer_status'] = self.status
        return to_dict