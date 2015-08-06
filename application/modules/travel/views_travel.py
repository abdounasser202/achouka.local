__author__ = 'wilrona'

from ...modules import *

from models_travel import TravelModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route('/settings/travel')
@login_required
@roles_required(('super_admin', 'admin'))
def Travel_Index():
    menu = 'settings'
    submenu = 'travel'

    travels = TravelModel.query()

    return render_template('/travel/index.html', **locals())