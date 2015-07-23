__author__ = 'wilrona'


from google.appengine.ext import ndb
from ..currency.models_currency import CurrencyModel


class DestinationModel(ndb.Model):
    code = ndb.StringProperty() # code de la ville
    name = ndb.StringProperty() # nom de la ville
    currency = ndb.KeyProperty(kind=CurrencyModel)