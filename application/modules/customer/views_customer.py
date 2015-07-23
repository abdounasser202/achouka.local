__author__ = 'wilrona'

from ...modules import *

from models_customer import CustomerModel
from forms_customer import FormCustomer

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route('/recording/customer')
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Customer_Index():
    menu = 'recording'
    submenu = 'customer'

    customers = CustomerModel.query()

    return render_template('customer/index.html', **locals())


@app.route('/recording/customer/edit', methods=['GET', 'POST'])
@app.route('/recording/customer/edit/<int:customer_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Customer_Edit(customer_id=None):
    menu = 'recording'
    submenu = 'customer'

    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    activity = ActivityModel()
    activity.user_modify = current_user.key
    activity.object = "DepartureModel"
    activity.time = function.datetime_convert(date_auto_nows)

    number_list = global_dial_code_custom
    nationalList = global_nationality_contry

    if customer_id:
        customer = CustomerModel.get_by_id(customer_id)
        form = FormCustomer(obj=customer)

    else:
        customer = CustomerModel()
        form = FormCustomer(request.form)

    customer_count = 0
    if form.validate_on_submit():

        customer_exist = CustomerModel.query(
            CustomerModel.first_name == form.first_name.data,
            CustomerModel.last_name == form.last_name.data,
            CustomerModel.birthday == function.date_convert(form.birthday.data)
        )
        customer_count = customer_exist.count()

        if customer_count >= 1 and not customer_id:
            customer_view = customer_exist.get()
            flash(u' This customer exist. ', 'danger')
        else:
            customer.first_name = form.first_name.data
            customer.last_name = form.last_name.data
            customer.birthday = function.date_convert(form.birthday.data)
            customer.passport_number = form.passport_number.data
            customer.nic_number = form.nic_number.data
            customer.profession = form.profession.data
            customer.email = form.email.data
            customer.nationality = form.nationality.data
            customer.phone = form.phone.data
            customer.dial_code = form.dial_code.data

            custom = customer.put()

            if customer_id:
                activity.identity = custom.id()
                activity.nature = 4
                activity.put()
                flash(u'Customer Updated!', 'success')
            else:
                activity.identity = custom.id()
                activity.nature = 1
                activity.put()
                flash(u'Customer Saved!', 'success')

            return redirect(url_for('Customer_Index'))

    return render_template('customer/edit.html', **locals())


@app.route('/Active_Customer/<int:customer_id>')
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Active_Customer(customer_id):
    custom = CustomerModel.get_by_id(customer_id)
    if custom.status is False:
        custom.status = True

    else:
        custom.status = False

    custom.put()

    flash(u' Customer Updated. ', 'success')
    return redirect(url_for("Customer_Index"))
