__author__ = 'wilrona'


from google.appengine.ext import ndb


class VesselModel(ndb.Model):
    name = ndb.StringProperty(required=True)
    capacity = ndb.IntegerProperty(required=True)
    immatricul = ndb.StringProperty()   