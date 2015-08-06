__author__ = 'wilrona'

from ...modules import *

from models_destination import DestinationModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route('/settings/destination')
@login_required
@roles_required(('admin', 'super_admin'))
def Destination_Index():
    menu = 'settings'
    submenu = 'destination'

    destinations = DestinationModel.query()

    return render_template('/destination/index.html', **locals())