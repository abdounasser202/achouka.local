__author__ = 'Wilrona'

from google.appengine.ext import ndb
from ..agency.models_agency import AgencyModel

class ConfigModel(ndb.Model):
    url_server = ndb.StringProperty()
    token_agency = ndb.StringProperty()
    local_ref = ndb.KeyProperty(kind=AgencyModel)


class SynchroModel(ndb.Model):
    date = ndb.DateProperty(auto_now=True)
    agency_synchro = ndb.KeyProperty(kind=AgencyModel)


class testModel(ndb.Model):
    test = ndb.StringProperty()