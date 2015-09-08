__author__ = 'Wilrona'

from google.appengine.ext import ndb
from ..agency.models_agency import AgencyModel

class ConfigModel(ndb.Model):
    url_server = ndb.StringProperty()
    token_agency = ndb.StringProperty()
    local_ref = ndb.KeyProperty(kind=AgencyModel)


class SynchroModel(ndb.Model):
    date = ndb.DateProperty(auto_now_add=True)
    agency_synchro = ndb.KeyProperty(kind=AgencyModel)
    time_all = ndb.TimeProperty(auto_now_add=True)
    time_departure = ndb.TimeProperty()
    time_customer = ndb.TimeProperty()
    time_customer_put = ndb.TimeProperty()
    time_ticket_sale_put = ndb.TimeProperty()
    time_ticket_sale_online = ndb.TimeProperty()
    time_return_and_doublons_foreign = ndb.TimeProperty()


class CronModel(ndb.Model):
    keys = ndb.IntegerProperty()
    model = ndb.StringProperty()