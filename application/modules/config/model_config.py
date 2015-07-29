__author__ = 'Wilrona'

from google.appengine.ext import ndb


class ConfigModel(ndb.Model):
    url_server = ndb.StringProperty()
    token_agency = ndb.StringProperty()
    id_local_agency = ndb.IntegerProperty()


class SynchroModel(ndb.Model):
    date = ndb.DateProperty(auto_now=True)