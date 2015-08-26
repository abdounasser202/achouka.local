__author__ = 'wilrona'

from ...modules import *

from models_ticket import AgencyModel, TicketTypeNameModel, ClassTypeModel, JourneyTypeModel
from ..ticket_type.models_ticket_type import TicketTypeModel, TravelModel
from ..transaction.models_transaction import TransactionModel, TicketModel, ExpensePaymentTransactionModel

from ..ticket_type.forms_ticket_type import FormSelectTicketType
from forms_ticket import FormTicket

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route('/manage/ticket')
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Ticket_Index():
    menu = 'recording'
    submenu = 'ticket'

    if not current_user.has_roles(('admin','super_admin')) and current_user.has_roles('manager_agency'):
        agency_user = AgencyModel.get_by_id(int(session.get('agence_id_local')))
        return redirect(url_for('Stat_View', agency_id=agency_user.key.id()))

    # Utiliser pour afficher la liste des agences avec leur ticket
    ticket_list = AgencyModel.query(
        AgencyModel.status == True
    )

    return render_template('ticket/index.html', **locals())


@app.route('/manage/ticket/statistics/<int:agency_id>')
@login_required
@roles_required(('super_admin', 'employee_POS'))
def Stat_View(agency_id):
    menu = 'recording'
    submenu = 'ticket'

    current_agency = AgencyModel.get_by_id(agency_id)

    # Traitement pour l'affichage du nombre de dernier ticket achete
    purchases_query = TicketModel.query(
        TicketModel.agency == current_agency.key,
        TicketModel.selling == False
    )

    ticket_purchase_tab = []
    for ticket in purchases_query:
        tickets = {}
        tickets['date'] = ticket.datecreate
        tickets['type'] = ticket.type_name
        tickets['class'] = ticket.class_name
        tickets['journey'] = ticket.journey_name
        tickets['number'] = 1
        tickets['travel'] = ticket.travel_ticket
        ticket_purchase_tab.append(tickets)

    grouper = itemgetter("date", "type", "class", "journey", "travel")

    ticket_purchase = []
    for key, grp in groupby(sorted(ticket_purchase_tab, key=grouper), grouper):
        temp_dict = dict(zip(["date", "type", "class", "journey", "travel"], key))
        temp_dict['number'] = 0
        for item in grp:
            temp_dict['number'] += item['number']
        ticket_purchase.append(temp_dict)

    # TYPE DE TICKET EN POSSESSION PAR L'AGENCE (etranger ou local)
    ticket_type_query = TicketTypeModel.query(
        TicketTypeModel.active == True
    )

    ticket_type_purchase_tab = []
    for ticket_type in ticket_type_query:
            tickets_type = {}
            tickets_type['name_ticket'] = ticket_type.name
            tickets_type['type'] = ticket_type.type_name
            tickets_type['class'] = ticket_type.class_name
            tickets_type['journey'] = ticket_type.journey_name
            tickets_type['number'] = TicketModel.query(
                TicketModel.travel_ticket == ticket_type.travel,
                TicketModel.class_name == ticket_type.class_name,
                TicketModel.journey_name == ticket_type.journey_name,
                TicketModel.type_name == ticket_type.type_name,
                TicketModel.selling == False,
                TicketModel.agency == current_agency.key
            ).count_async().get_result()
            tickets_type['travel'] = ticket_type.travel
            ticket_type_purchase_tab.append(tickets_type)

    grouper = itemgetter("name_ticket", "type", "class", "journey", "travel")

    ticket_type_purchase = []
    for key, grp in groupby(sorted(ticket_type_purchase_tab, key=grouper), grouper):
        temp_dict = dict(zip(["name_ticket", "type", "class", "journey", "travel"], key))
        temp_dict['number'] = 0
        for item in grp:
            temp_dict['number'] += item['number']
        ticket_type_purchase.append(temp_dict)

    return render_template('ticket/stat-view.html', **locals())

