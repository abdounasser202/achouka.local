__author__ = 'wilrona'

from google.appengine.ext import ndb


class ProfilModel(ndb.Model):
    name = ndb.StringProperty()
    standard = ndb.BooleanProperty(default=False)
    enable = ndb.BooleanProperty(default=True)
