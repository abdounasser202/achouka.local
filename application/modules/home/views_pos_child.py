__author__ = 'Vercossa'

from ...modules import *

from ..customer.models_customer import CustomerModel
from ..ticket.models_ticket import (TicketPoly, TicketModel, TicketTypeNameModel, DepartureModel,
                                    JourneyTypeModel, ClassTypeModel, AgencyModel, QuestionModel, TicketQuestion)

from ..customer.forms_customer import FormCustomerPOS


cache = Cache(app)


@app.route('/create_customer_child_ticket/<int:ticket_id>', methods=['GET', 'POST'])
@app.route('/create_customer_child_ticket/<int:ticket_id>/<int:departure_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('employee_POS', 'super_admin'))
def create_customer_child_ticket(ticket_id=None, departure_id=None):

    departure_get = DepartureModel.get_by_id(departure_id)
    age = date_age
    return render_template('/pos_child/pos_modal.html', **locals())