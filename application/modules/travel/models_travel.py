__author__ = 'wilrona'

from google.appengine.ext import ndb
from ..destination.models_destination import DestinationModel

class TravelModel(ndb.Model):
    time = ndb.TimeProperty()
    destination_start = ndb.KeyProperty(kind=DestinationModel)
    destination_check = ndb.KeyProperty(kind=DestinationModel)
    datecreate = ndb.DateTimeProperty(auto_now_add=True)
    date_update = ndb.DateProperty(auto_now=True)
