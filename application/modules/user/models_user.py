__author__ = 'wilrona'

from google.appengine.ext import ndb
from ..currency.models_currency import CurrencyModel
from ..agency.models_agency import AgencyModel
from ..profil.models_profil import ProfilModel

from itertools import groupby
from operator import itemgetter

class UserModel(ndb.Model):

    password = ndb.StringProperty()
    reset_password_token = ndb.StringProperty()

    email = ndb.StringProperty()
    confirmed_at = ndb.DateTimeProperty()
    date_create = ndb.DateTimeProperty(auto_now_add=True)

    is_enabled = ndb.BooleanProperty(default=True)
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    phone = ndb.StringProperty()
    dial_code = ndb.StringProperty()
    logged = ndb.BooleanProperty(default=False)
    date_last_logged = ndb.DateTimeProperty()

    agency = ndb.KeyProperty(kind=AgencyModel)
    currency = ndb.KeyProperty(kind=CurrencyModel)
    profil = ndb.KeyProperty(kind=ProfilModel)

    def is_active(self):
        return self.is_enabled

    def is_authenticated(self):
        return self.logged

    def is_anonymous(self):
        return False

    def full_name(self):
        full_name = ''+str(self.last_name)+' '+str(self.first_name)+''
        return full_name

    def agencys(self):
        agency = None
        if self.agency:
            agency_data = AgencyModel.get_by_id(self.agency.id())
            agency = agency_data.name
        else:
            agency = 'Super Agency'
        return agency

    def have_agency(self): #verifie que l'utilisateur courant a une agence pour faire des ventes
        if self.agency:
            return True
        return False

    def have_credit(self): #verifie que l'agence de l'utilisateur courant a des tickets a vendre
        from ..ticket.models_ticket import TicketModel
        user_agence = AgencyModel.get_by_id(self.agency.id())

        user_ticket = TicketModel.query(
            TicketModel.agency == user_agence.key
        ).count()

        if user_ticket >= 1:
            return True

        return False

    def has_roles(self, *requirements):

        user_role = UserRoleModel.query(
            UserRoleModel.user_id == self.key
        )

        user_roles = [role.role_id.get().name for role in user_role]

        # has_role() accepts a list of requirements
        for requirement in requirements:
            if isinstance(requirement, (list, tuple)):
                # this is a tuple_of_role_names requirement
                tuple_of_role_names = requirement
                authorized = False
                for role_name in tuple_of_role_names:
                    if role_name in user_roles:
                        # tuple_of_role_names requirement was met: break out of loop
                        authorized = True
                        break
                if not authorized:
                    return False                    # tuple_of_role_names requirement failed: return False
            else:
                # this is a role_name requirement
                role_name = requirement
                # the user must have this role
                if not role_name in user_roles:
                    return False                    # role_name requirement failed: return False

        # All requirements have been met: return True
        return True

    def remaining_ticket(self):
        if self.agency:
            agency_user = AgencyModel.get_by_id(self.agency.id())
            number = agency_user.TicketUnsold()
        else:
            number = 'No Ticket'
        return number+' Available'


    def ticket_number_selling(self, user_ticket_query=None, local_agency=True):
        from ..transaction.models_transaction import ExpensePaymentTransactionModel, TicketModel

        if not user_ticket_query:
            user_ticket_query = TicketModel.query(
                TicketModel.ticket_seller == self.key,
                TicketModel.selling == True
            )

        # recupere le montant des tickets qui n'ont pas encore de transaction de paiement
        ticket_number = 0
        for ticket in user_ticket_query:
            if local_agency:
                if ticket.travel_ticket.get().destination_start == self.agency.get().destination:
                    expensepayment_query = ExpensePaymentTransactionModel.query(
                        ExpensePaymentTransactionModel.ticket == ticket.key
                    )
                    number = 0
                    for expense in expensepayment_query:
                        if expense.transaction.get().is_payment is True and expense.transaction.get().destination == self.agency.get().destination and expense.is_difference is False:
                            number += 1

                    if number == 0:
                        ticket_number += 1
            else:
                if ticket.travel_ticket.get().destination_start != self.agency.get().destination:
                    expensepayment_query = ExpensePaymentTransactionModel.query(
                        ExpensePaymentTransactionModel.ticket == ticket.key
                    )
                    number = 0
                    for expense in expensepayment_query:
                        if expense.transaction.get().is_payment is True and expense.is_difference is False:
                            number += 1

                    if number == 0:
                        ticket_number += 1

        return ticket_number

    #Montant des tickets qui n'ont pas encore de transaction de paiement
    def ticket_no_transaction_amount(self, list_ticket_travel_query, local_agency=True):
        from ..transaction.models_transaction import ExpensePaymentTransactionModel

        ticket_no_transaction_amount = 0
        for ticket in list_ticket_travel_query:
            if local_agency:
                if ticket.travel_ticket.get().destination_start == self.agency.get().destination:
                    expensepayment_query = ExpensePaymentTransactionModel.query(
                        ExpensePaymentTransactionModel.ticket == ticket.key
                    )
                    number = 0
                    for transaction_line in expensepayment_query:
                        if transaction_line.transaction.get().is_payment is True and transaction_line.transaction.get().destination == self.agency.get().destination and transaction_line.is_difference is False:
                            number += 1

                    if number == 0:
                       ticket_no_transaction_amount += ticket.sellprice
            else:
                if ticket.travel_ticket.get().destination_start != self.agency.get().destination:
                    expensepayment_query = ExpensePaymentTransactionModel.query(
                        ExpensePaymentTransactionModel.ticket == ticket.key
                    )
                    number = 0
                    for transaction_line in expensepayment_query:
                        if transaction_line.transaction.get().is_payment is True and transaction_line.transaction.get().destination != self.agency.get().destination and transaction_line.is_difference is False:
                            number += 1

                    if number == 0:
                       ticket_no_transaction_amount += ticket.sellprice

        return ticket_no_transaction_amount

    # Montant des tickets qui ont des transactions et qui sont deficitaire
    def ticket_transaction_amount(self, list_ticket_travel_query, local_agency=True):
        from ..transaction.models_transaction import ExpensePaymentTransactionModel

        ticket_transaction_amount = 0
        for ticket in list_ticket_travel_query:
            if local_agency:
                if ticket.travel_ticket.get().destination_start == self.agency.get().destination:
                    expensepayment_query = ExpensePaymentTransactionModel.query(
                        ExpensePaymentTransactionModel.ticket == ticket.key
                    )
                    number = 0
                    transaction_amount = 0
                    for transaction_line in expensepayment_query:
                        if transaction_line.transaction.get().is_payment is True and transaction_line.transaction.get().destination == self.agency.get().destination and transaction_line.is_difference is False:
                            number += 1
                            transaction_amount += transaction_line.amount

                    if number >= 1 and ticket.sellprice > transaction_amount:
                        ticket_transaction_amount += ticket.sellprice-transaction_amount
            else:
                if ticket.travel_ticket.get().destination_start != self.agency.get().destination:
                    expensepayment_query = ExpensePaymentTransactionModel.query(
                        ExpensePaymentTransactionModel.ticket == ticket.key
                    )
                    number = 0
                    transaction_amount = 0
                    for transaction_line in expensepayment_query:
                        if transaction_line.transaction.get().is_payment is True and transaction_line.transaction.get().destination != self.agency.get().destination and transaction_line.is_difference is False:
                            number += 1
                            transaction_amount += transaction_line.amount

                    if number >= 1 and ticket.sellprice > transaction_amount:
                        ticket_transaction_amount += ticket.sellprice - transaction_amount

        return ticket_transaction_amount


    # Montant des tickets etranger et le nombre de ticket (pluriel)
    def foreign_escrow_and_number_ticket(self, travel_id=None):
        from ..ticket.models_ticket import TicketModel, TravelModel

        if travel_id:
            travel = TravelModel.get_by_id(int(travel_id))
            ticket_travel_foreign_query = TicketModel.query(
                TicketModel.selling == True,
                TicketModel.travel_ticket == travel.key,
                TicketModel.ticket_seller == self.key
            )
        else:
            ticket_travel_foreign_query = TicketModel.query(
                TicketModel.selling == True,
                TicketModel.ticket_seller == self.key
            )

        ticket_travel_foreign_tab = []

        for ticket_foreign in ticket_travel_foreign_query:

            if ticket_foreign.travel_ticket.get().destination_start != self.agency.get().destination:

                list_ticket_travel_query = TicketModel.query(
                    TicketModel.travel_ticket == ticket_foreign.travel_ticket,
                    TicketModel.ticket_seller == self.key,
                    TicketModel.selling == True
                )

                #Nombre de ticket
                ticket_number = self.ticket_number_selling(list_ticket_travel_query, False)

                # recupere le montant des tickets qui n'ont pas encore de transaction de paiement
                ticket_no_transaction_amount = self.ticket_no_transaction_amount(list_ticket_travel_query, False)


                # recupere le montant des tickets qui ont des transactions et qui sont deficitaire
                ticket_transaction_amount = self.ticket_transaction_amount(list_ticket_travel_query, False)

                # sommes des montants retournes
                escrow = ticket_no_transaction_amount + ticket_transaction_amount

                tickets = {}
                tickets['number'] = ticket_number
                tickets['escrow'] = escrow
                tickets['travel'] = ticket_foreign.travel_ticket
                tickets['ticket_seller'] = ticket_foreign.ticket_seller
                ticket_travel_foreign_tab.append(tickets)

        grouper = itemgetter("travel", "ticket_seller")
        user_tickets = []
        for key, grp in groupby(sorted(ticket_travel_foreign_tab, key=grouper), grouper):
            temp_dict = dict(zip(["travel", "ticket_seller"], key))
            temp_dict['number'] = 0
            temp_dict['escrow'] = 0
            for item in grp:
                temp_dict['number'] = item['number']
                temp_dict['escrow'] = item['escrow']
            user_tickets.append(temp_dict)

        return user_tickets


    # Montant des tickets vendus et des restes a payer de l'utilisateur
    def escrow_amount(self):
        from ..ticket.models_ticket import TicketModel

        user_ticket_query = TicketModel.query(
            TicketModel.ticket_seller == self.key,
            TicketModel.selling == True
        )

        # recupere le montant des tickets qui n'ont pas encore de transaction de paiement
        ticket_no_transaction_amount = self.ticket_no_transaction_amount(user_ticket_query)

        # recupere le montant des tickets qui ont des transactions et qui sont deficitaire
        ticket_transaction_amount = self.ticket_transaction_amount(user_ticket_query)

        # sommes des montants retournes
        escrow = ticket_no_transaction_amount + ticket_transaction_amount

        if escrow != 0:
            escrow = '{:,}'.format(escrow).replace(',', ' ')
            return str(escrow)+" "+self.agency.get().destination.get().currency.get().code
        else:
            return None


    #Liste des Tickets a solder par l'utilisateur
    def ticket_user_no_transaction_payment(self):
        from ..transaction.models_transaction import ExpensePaymentTransactionModel, TicketModel

        user_ticket_query = TicketModel.query(
            TicketModel.ticket_seller == self.key,
            TicketModel.selling == True
        )

        user_tickets_tab = []

        for ticket in user_ticket_query:
            if ticket.travel_ticket.get().destination_start == self.agency.get().destination:
                expensepayment_query = ExpensePaymentTransactionModel.query(
                    ExpensePaymentTransactionModel.ticket == ticket.key
                )
                number = 0
                for transaction_line in expensepayment_query:
                    if transaction_line.transaction.get().is_payment is True and transaction_line.is_difference is False:
                        number += 1

                tickets = {}
                if number == 0:
                    tickets['type'] = ticket.type_name
                    tickets['class'] = ticket.class_name
                    tickets['travel'] = ticket.travel_ticket
                    tickets['journey'] = ticket.journey_name
                    tickets['number'] = 1
                    tickets['amount'] = ticket.sellprice
                    tickets['currency'] = ticket.sellpriceCurrency
                    user_tickets_tab.append(tickets)

        grouper = itemgetter("travel", "type", "class", "journey", "currency")

        user_tickets = []
        for key, grp in groupby(sorted(user_tickets_tab, key=grouper), grouper):
            temp_dict = dict(zip(["travel", "type", "class", "journey", "currency"], key))
            temp_dict['number'] = 0
            temp_dict['amount'] = 0
            for item in grp:
                temp_dict['number'] += item['number']
                temp_dict['amount'] += item['amount']
            user_tickets.append(temp_dict)

        return user_tickets

    # liste des tickets dont le solde n'est pas encore fini
    def ticket_user_transaction_payment_no_solved(self):
        from ..transaction.models_transaction import ExpensePaymentTransactionModel, TicketModel

        user_ticket_query = TicketModel.query(
            TicketModel.ticket_seller == self.key,
            TicketModel.selling == True
        )

        user_tickets_tab = []

        for ticket in user_ticket_query:
            if ticket.travel_ticket.get().destination_start == self.agency.get().destination:
                expensepayment_query = ExpensePaymentTransactionModel.query(
                    ExpensePaymentTransactionModel.ticket == ticket.key
                )

                number = 0
                transaction_amount = 0
                for transaction_line in expensepayment_query:
                    if transaction_line.transaction.get().is_payment is True and transaction_line.is_difference is False:
                        number += 1
                        transaction_amount += transaction_line.amount

                tickets = {}
                if number >= 1 and ticket.sellprice > transaction_amount:
                    tickets['type'] = ticket.type_name
                    tickets['class'] = ticket.class_name
                    tickets['travel'] = ticket.travel_ticket
                    tickets['journey'] = ticket.journey_name
                    tickets['number'] = 1
                    tickets['amount'] = ticket.sellprice
                    tickets['balance'] = ticket.sellprice - transaction_amount
                    tickets['currency'] = ticket.sellpriceCurrency
                    user_tickets_tab.append(tickets)

        return user_tickets_tab


class RoleModel(ndb.Model):
    name = ndb.StringProperty()
    visible = ndb.BooleanProperty(default=True)


class UserRoleModel(ndb.Model):
    user_id = ndb.KeyProperty(kind=UserModel)
    role_id = ndb.KeyProperty(kind=RoleModel)


class ProfilRoleModel(ndb.Model):
    profil_id = ndb.KeyProperty(kind=ProfilModel)
    role_id = ndb.KeyProperty(kind=RoleModel)
