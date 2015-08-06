__author__ = 'wilrona'

from ...modules import *

from models_currency import CurrencyModel


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@roles_required(('admin', 'super_admin'))
@app.route('/settings/currency')
@login_required
def Currency_Index():
    menu = 'settings'
    submenu = 'currency'

    currencys = CurrencyModel.query()

    return render_template('/currency/index.html', **locals())