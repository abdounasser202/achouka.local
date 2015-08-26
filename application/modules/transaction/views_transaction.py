__author__ = 'wilrona'

from ...modules import *

from ..transaction.models_transaction import TransactionModel, AgencyModel, UserModel, TicketModel, ExpensePaymentTransactionModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route('/manage/transaction')
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Transaction_Index():
    menu = 'recording'
    submenu = 'transaction'

    if not current_user.has_roles(('admin','super_admin')) and current_user.has_roles('manager_agency'):
        agency_user = AgencyModel.get_by_id(int(session.get('agence_id_local')))
        return redirect(url_for('Transaction_Agency', agency_id=agency_user.key.id()))

    List_agency = AgencyModel.query()

    return render_template('/transaction/index.html', **locals())

@app.route('/manage/transaction/stat/<int:agency_id>')
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Transaction_Agency(agency_id):
    menu = 'recording'
    submenu = 'transaction'

    current_agency = AgencyModel.get_by_id(agency_id)

    #liste des transaction de l'agence
    transaction_agency_query = TransactionModel.query(
        TransactionModel.agency == current_agency.key,
        TransactionModel.transaction_admin == False
    )

    # Liste des utilisateurs de l'agence
    user_agency = UserModel.query(
        UserModel.agency == current_agency.key
    )

    return render_template('/transaction/stat-views.html', **locals())


@app.route('/Transaction_detail')
@app.route('/Transaction_detail/<int:transaction_id>')
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Transaction_detail(transaction_id=None):

    current_transaction_get_id = TransactionModel.get_by_id(transaction_id)

    transaction_detail = []
    for transaction in current_transaction_get_id.relation_parent_child():
        transactions = {}
        transactions['type'] = transaction.ticket.get().type_name
        transactions['journey'] = transaction.ticket.get().journey_name
        transactions['class'] = transaction.ticket.get().class_name
        transactions['travel'] = transaction.ticket.get().travel_ticket
        transactions['amount'] = transaction.amount
        transactions['currency'] = transaction.ticket.get().sellpriceAgCurrency.get().code
        transaction_detail.append(transactions)

    grouper = itemgetter("type", "class", "journey", "travel", "currency")

    detail_transaction = []
    for key, grp in groupby(sorted(transaction_detail, key=grouper), grouper):
        temp_dict = dict(zip(["type", "class", "journey", "travel", "currency"], key))
        temp_dict['number'] = 0
        temp_dict['amount'] = 0
        for item in grp:
            temp_dict['number'] += 1
            temp_dict['amount'] += item['amount']
        detail_transaction.append(temp_dict)

    return render_template('/transaction/transaction_details.html', **locals())


@app.route('/Transaction_user', methods=["GET", "POST"])
@app.route('/Transaction_user/<int:user_id>', methods=["GET", "POST"])
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Transaction_user(user_id=None):

    user_get_id = UserModel.get_by_id(user_id)

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    return render_template('/transaction/transaction_user.html', **locals())


@app.route('/Transaction_foreign_user', methods=["GET", "POST"])
@app.route('/Transaction_foreign_user/<int:user_id>/<int:travel_id>', methods=["GET", "POST"])
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Transaction_foreign_user(user_id=None, travel_id=None):

    from ..travel.models_travel import TravelModel

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    user_get_id = UserModel.get_by_id(user_id)
    travel_get_id = TravelModel.get_by_id(int(travel_id))

    ticket_user_query = TicketModel.query(
        TicketModel.ticket_seller == user_get_id.key,
        TicketModel.travel_ticket == travel_get_id.key,
        TicketModel.is_count == True
    )

    user_tickets_tab = []
    user_tickets_tab_unsolved_payment = []

    for ticket in ticket_user_query:
        expensepayment_query = ExpensePaymentTransactionModel.query(
            ExpensePaymentTransactionModel.ticket == ticket.key
        )
        #RECUPERATION DES TICKETS QUE L'ON VA SOLDER
        number_attend_payment = 0
        for transaction_line in expensepayment_query:
            if transaction_line.transaction.get().is_payment is True and transaction_line.is_difference is False:
                number_attend_payment += 1

        tickets = {}
        if number_attend_payment == 0:
            tickets['id'] = ticket.key.id()
            tickets['type'] = ticket.type_name
            tickets['class'] = ticket.class_name
            tickets['journey'] = ticket.journey_name
            tickets['number'] = 1
            tickets['amount'] = ticket.sellprice
            tickets['currency'] = ticket.sellpriceCurrency
            user_tickets_tab.append(tickets)

        #RECUPERATION DES TICKETS NON SOLDE
        number_unsolved_payment = 0
        transaction_amount = 0
        for transaction_line in expensepayment_query:
            if transaction_line.transaction.get().is_payment is True and transaction_line.is_difference is False:
                number_unsolved_payment += 1
                transaction_amount += transaction_line.amount

        tickets = {}
        if number_unsolved_payment >= 1 and ticket.sellprice > transaction_amount:
            tickets['id'] = ticket.key.id()
            tickets['type'] = ticket.type_name
            tickets['class'] = ticket.class_name
            tickets['journey'] = ticket.journey_name
            tickets['number'] = 1
            tickets['amount'] = ticket.sellprice
            tickets['balance'] = ticket.sellprice - transaction_amount
            tickets['currency'] = ticket.sellpriceCurrency
            user_tickets_tab_unsolved_payment.append(tickets)

    grouper = itemgetter("type", "class", "journey", "currency")

    user_tickets = []
    for key, grp in groupby(sorted(user_tickets_tab, key=grouper), grouper):
        temp_dict = dict(zip(["type", "class", "journey", "currency"], key))
        temp_dict['number'] = 0
        temp_dict['amount'] = 0
        for item in grp:
            temp_dict['number'] += item['number']
            temp_dict['amount'] += item['amount']
        user_tickets.append(temp_dict)

    return render_template('/transaction/transaction_foreign_user.html', **locals())

