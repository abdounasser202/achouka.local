__author__ = 'wilrona'


from google.appengine.ext import ndb
from ..currency.models_currency import CurrencyModel, EquivalenceModel
from ..travel.models_travel import TravelModel


class TicketTypeNameModel(ndb.Model):
    name = ndb.StringProperty()
    is_child = ndb.BooleanProperty(default=False)
    default = ndb.BooleanProperty(default=False)
    special = ndb.BooleanProperty(default=False)


class JourneyTypeModel(ndb.Model):
    name = ndb.StringProperty()
    default = ndb.BooleanProperty(default=False)
    returned = ndb.BooleanProperty(default=False)


class ClassTypeModel(ndb.Model):
    name = ndb.StringProperty()
    default = ndb.BooleanProperty(default=False)


class TicketTypeModel(ndb.Model):
    name = ndb.StringProperty()
    type_name = ndb.KeyProperty(kind=TicketTypeNameModel)
    journey_name = ndb.KeyProperty(kind=JourneyTypeModel)
    class_name = ndb.KeyProperty(kind=ClassTypeModel)
    price = ndb.FloatProperty()
    currency = ndb.KeyProperty(kind=CurrencyModel)
    active = ndb.BooleanProperty(default=False)
    travel = ndb.KeyProperty(kind=TravelModel)

    def get_price(self, current_user):

        #Traitement des prix en fonction de la devise.
        db_currency = CurrencyModel.get_by_id(self.currency.id())
        us_currency = current_user.get_currency_info()


        custom_equi = EquivalenceModel.query(
            EquivalenceModel.currencyRate == db_currency.key,
            EquivalenceModel.currencyEqui == us_currency.key
        ).get()

        if not custom_equi:
            price = self.price
            currency = db_currency.code
        else:
            price = self.price*custom_equi.value
            currency = us_currency.code

        new_price = str(price)+" "+currency

        return new_price