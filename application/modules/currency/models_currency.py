__author__ = 'wilrona'


from google.appengine.ext import ndb


class CurrencyModel(ndb.Model):
    code = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)


class EquivalenceModel(ndb.Model):
    currencyRate = ndb.KeyProperty(kind=CurrencyModel)
    value = ndb.FloatProperty(required=True)
    currencyEqui = ndb.KeyProperty(kind=CurrencyModel)