__author__ = 'wilrona'

from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel

from ..user.models_user import UserModel
from ..agency.models_agency import AgencyModel
from ..currency.models_currency import CurrencyModel, EquivalenceModel
from ..customer.models_customer import CustomerModel
from ..departure.models_departure import DepartureModel, TravelModel
from ..ticket_type.models_ticket_type import ClassTypeModel, TicketTypeNameModel, JourneyTypeModel
from ..question.models_question import QuestionModel


class TicketPoly(polymodel.PolyModel):

    sellpriceAg = ndb.FloatProperty()
    sellpriceAgCurrency = ndb.KeyProperty(kind=CurrencyModel)

    type_name = ndb.KeyProperty(kind=TicketTypeNameModel)
    class_name = ndb.KeyProperty(kind=ClassTypeModel)
    journey_name = ndb.KeyProperty(kind=JourneyTypeModel)
    travel_ticket = ndb.KeyProperty(kind=TravelModel)

    agency = ndb.KeyProperty(kind=AgencyModel)
    is_prepayment = ndb.BooleanProperty(default=True)
    statusValid = ndb.BooleanProperty(default=True)
    is_return = ndb.BooleanProperty(default=False)

    selling = ndb.BooleanProperty(default=False)
    is_ticket = ndb.BooleanProperty(default=True)
    date_reservation = ndb.DateTimeProperty()
    sellprice = ndb.FloatProperty()
    sellpriceCurrency = ndb.KeyProperty(kind=CurrencyModel)

    customer = ndb.KeyProperty(kind=CustomerModel)
    departure = ndb.KeyProperty(kind=DepartureModel)

    ticket_seller = ndb.KeyProperty(kind=UserModel)
    e_ticket_seller = ndb.KeyProperty(kind=UserModel)
    is_boarding = ndb.BooleanProperty(default=False)

    datecreate = ndb.DateTimeProperty()


class TicketModel(TicketPoly):

    upgrade_parent = ndb.KeyProperty(kind=TicketPoly)
    is_upgrade = ndb.BooleanProperty(default=False)
    is_count = ndb.BooleanProperty(default=True)
    parent_return = ndb.KeyProperty(kind=TicketPoly)

    def answer_question(self):
        answer = TicketQuestion.query(
            TicketQuestion.ticket_id == self.key
        )
        return answer

    def make_to_dict(self):
        to_dict = {}

        to_dict['ticket_id'] = self.key.id()
        to_dict['date_reservation'] = str(self.date_reservation)
        to_dict['sellprice'] = self.sellprice
        to_dict['sellpriceCurrency'] = self.sellpriceCurrency.id()

        to_dict['customer'] = self.customer.id()
        to_dict['departure'] = self.departure.id()
        to_dict['ticket_seller'] = self.ticket_seller.id()
        to_dict['agency'] = self.agency.id()

        to_dict['is_prepayment'] = self.is_prepayment
        to_dict['statusValid'] = self.statusValid
        to_dict['is_return'] = self.is_return

        to_dict['travel_ticket'] = self.travel_ticket.id()
        to_dict['is_boarding'] = self.is_boarding

        upgrade = False
        if self.is_upgrade:
            to_dict['is_upgrade'] = self.is_upgrade
            to_dict['upgrade_parent'] = self.upgrade_parent.id()
            to_dict['is_count'] = self.is_count
            upgrade = True
        to_dict['child_upgrade'] = upgrade

        from ..transaction.models_transaction import ExpensePaymentTransactionModel

        transactions = ExpensePaymentTransactionModel.query(
            ExpensePaymentTransactionModel.ticket == self.key,
            ExpensePaymentTransactionModel.is_difference == True
        )
        to_dict['transaction'] = []
        for transaction in transactions:
            trans = {}
            trans['amount'] = transaction.transaction.get().amount
            trans['is_payment'] = transaction.transaction.get().is_payment
            trans['reason'] = transaction.transaction.get().reason
            to_dict['transaction'].append(trans)

        question_answer = TicketQuestion.query(
            TicketQuestion.ticket_id == self.key
        )

        to_dict['ticket_question'] = []
        for question in question_answer:
            quest = {}
            quest['question_id'] = question.question_id.id()
            quest['response'] = question.respnse
            to_dict['ticket_question'].append(quest)

        return to_dict


class TicketQuestion(ndb.Model):
    question_id = ndb.KeyProperty(kind=QuestionModel)
    ticket_id = ndb.KeyProperty(kind=TicketModel)
    response = ndb.BooleanProperty(default=False)
