__author__ = 'wilrona'

from google.appengine.ext import ndb
from ..destination.models_destination import DestinationModel
from ..currency.models_currency import CurrencyModel


from itertools import groupby
from operator import itemgetter


class AgencyModel(ndb.Model):
    name = ndb.StringProperty()
    country = ndb.StringProperty()
    phone = ndb.StringProperty()
    fax = ndb.StringProperty()
    address = ndb.StringProperty()
    reduction = ndb.FloatProperty()
    status = ndb.BooleanProperty(default=False)
    destination = ndb.KeyProperty(kind=DestinationModel)
    is_achouka = ndb.BooleanProperty()
    is_coorporate = ndb.BooleanProperty()

    def TicketCount(self):
        from ..ticket.models_ticket import TicketModel

        ticket = TicketModel.query(
            TicketModel.agency == self.key
        ).count()

        if ticket <= 1:
            title = 'ticket'
        else:
            title = ' tickets'

        return str(ticket)+' '+title

    def TicketUnsold(self):
        from ..ticket.models_ticket import TicketModel

        ticket = TicketModel.query(
            TicketModel.agency == self.key,
            TicketModel.selling == False
        ).count()

        if ticket <= 1:
            title = 'ticket'
        else:
            title = ' tickets'

        return str(ticket)+' '+str(title)

    def DateLastPurchase(self):
        from ..ticket.models_ticket import TicketModel

        ticket = TicketModel.query(
            TicketModel.agency == self.key
        ).order(-TicketModel.datecreate)

        ticket = ticket.get()

        if ticket:
            date = ticket.datecreate
        else:
            date = None

        return date

    def escrow_amount(self, value=False):
        from ..transaction.models_transaction import TransactionModel

        entry_query = TransactionModel.query(
            TransactionModel.is_payment == True,
            TransactionModel.agency == self.key,
            TransactionModel.transaction_admin == value,
            TransactionModel.destination == self.destination
        )

        entry_amount = 0
        for entry in entry_query:
            entry_amount += entry.amount

        expense_query = TransactionModel.query(
            TransactionModel.is_payment == False,
            TransactionModel.agency == self.key,
            TransactionModel.transaction_admin == False,
            TransactionModel.destination == self.destination
        )

        expense_amount = 0
        for expense in expense_query:
            expense_amount += expense.amount

        escrow = entry_amount - expense_amount

        return escrow

    # Montant des tickets etrangers (defaut POS, True = Agency)
    def escrow_amount_foreign(self, value=False):
        from ..transaction.models_transaction import TransactionModel

        destination_transaction_query = TransactionModel.query(
            TransactionModel.agency == self.key,
            TransactionModel.destination != self.destination
        )

        destinations_table = []
        for transaction in destination_transaction_query:

            entry_query = TransactionModel.query(
                TransactionModel.is_payment == True,
                TransactionModel.agency == self.key,
                TransactionModel.transaction_admin == value,
                TransactionModel.destination == transaction.destination
            )

            # SOMMES DES ENTRES
            entry_amount = 0
            for entry in entry_query:
                entry_amount += entry.amount

            expense_query = TransactionModel.query(
                TransactionModel.is_payment == False,
                TransactionModel.agency == self.key,
                TransactionModel.transaction_admin == False,
                TransactionModel.destination == transaction.destination
            )

            # SOMMES DES SORTIES
            expense_amount = 0
            for expense in expense_query:
                expense_amount += expense.amount

            # TOTAL RETENU
            amount = entry_amount - expense_amount

            trans_init = {}
            trans_init['amount'] = amount
            trans_init['destination'] = transaction.destination
            trans_init['agency'] = transaction.agency

            destinations_table.append(trans_init)

        grouper = itemgetter("destination", "agency")

        # REGROUPEMENT DES MONTANTS PAR DESTINATION
        escrow_amount_foreigns = []
        for key, grp in groupby(sorted(destinations_table, key=grouper), grouper):
            temp_dict = dict(zip(["destination", "agency"], key))
            temp_dict['amount'] = 0
            for item in grp:
                temp_dict['amount'] = item['amount']
            escrow_amount_foreigns.append(temp_dict)

        return escrow_amount_foreigns
