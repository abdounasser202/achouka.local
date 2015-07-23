__author__ = 'wilrona'

from google.appengine.ext import ndb

from ..agency.models_agency import AgencyModel, DestinationModel
from ..ticket.models_ticket import TicketModel, UserModel


class TransactionModel(ndb.Model):
    reason = ndb.StringProperty()
    amount = ndb.FloatProperty()
    is_payment = ndb.BooleanProperty()
    agency = ndb.KeyProperty(kind=AgencyModel)
    destination = ndb.KeyProperty(kind=DestinationModel)
    transaction_date = ndb.DateTimeProperty()
    user = ndb.KeyProperty(kind=UserModel)
    transaction_admin = ndb.BooleanProperty(default=False)

    def relation_parent_child(self):
        relation = ExpensePaymentTransactionModel.query(
            ExpensePaymentTransactionModel.transaction == self.key
        )
        return relation


class ExpensePaymentTransactionModel(ndb.Model):
    transaction = ndb.KeyProperty(kind=TransactionModel)
    ticket = ndb.KeyProperty(kind=TicketModel)
    amount = ndb.FloatProperty()
    is_difference = ndb.BooleanProperty(default=False) # si la transaction est different du montant du ticket