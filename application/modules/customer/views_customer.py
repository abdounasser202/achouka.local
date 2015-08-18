__author__ = 'wilrona'

from ...modules import *

from models_customer import CustomerModel
from forms_customer import FormCustomer

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route('/manage/customer')
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Customer_Index():
    menu = 'recording'
    submenu = 'customer'

    customers = CustomerModel.query()

    return render_template('customer/index.html', **locals())


@app.route('/manage/customer/edit', methods=['GET', 'POST'])
@app.route('/manage/customer/edit/<int:customer_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Customer_Edit(customer_id=None):
    menu = 'recording'
    submenu = 'customer'

    number_list = global_dial_code_custom
    nationalList = global_nationality_contry


    customer = CustomerModel.get_by_id(customer_id)
    form = FormCustomer(obj=customer)

    return render_template('customer/edit.html', **locals())

