__author__ = 'wilrona'

from ...modules import *
from forms_vessel import FormVessel
from models_vessel import VesselModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route('/settings/vessel')
@login_required
@roles_required(('admin', 'super_admin'))
def Vessel_Index():
    menu = 'settings'
    submenu = 'vessel'

    vessels = VesselModel.query()

    return render_template('/vessel/index.html', **locals())


