__author__ = 'wilrona'

from ...modules import *

from models_ticket_type import TicketTypeModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route('/settings/ticket')
@login_required
@roles_required(('admin', 'super_admin'))
def TicketType_Index():
    menu = 'settings'
    submenu = 'tickettype'

    tickettype = TicketTypeModel.query()

    return render_template('/tickettype/index.html', **locals())