__author__ = 'wilrona'

from ...modules import *
from google.appengine.ext import ndb

from models_user import UserModel, RoleModel, UserRoleModel, CurrencyModel, AgencyModel, ProfilRoleModel, ProfilModel
from forms_user import FormRegisterUserAdmin, FormEditUserAdmin, FormEditUser, FormRegisterUser

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route('/creationsuperadmin', methods=['GET', 'POST'])
def Super_Admin_Create():

    form = FormRegisterUserAdmin(request.form)

    if form.validate_on_submit():
        User = UserModel()

        role = RoleModel.query(RoleModel.name == 'super_admin').get()
        if not role:
            role = RoleModel()
            role.name = 'super_admin'
            role.visible = False

            role = role.put()
            role = RoleModel.get_by_id(role.id())

        UserRole = UserRoleModel()

        currency = CurrencyModel.query(
            CurrencyModel.code == form.currency.data
        ).get()

        if not currency:
            CurrencyCreate = CurrencyModel()
            CurrencyCreate.code = form.currency.data
            CurrencyCreate.name = 'Franc CFA'
            currencyCreate = CurrencyCreate.put()
            currencyCreate = CurrencyModel.get_by_id(currencyCreate.id())
        else:
            currencyCreate = currency

        if role:
            User.first_name = form.first_name.data
            User.last_name = form.last_name.data
            User.email = form.email.data
            User.currency = currencyCreate.key

            password = hashlib.sha224(form.password.data).hexdigest()
            User.password = password

            UserCreate = User.put()
            UserCreate = UserModel.get_by_id(UserCreate.id())

            UserRole.role_id = role.key
            UserRole.user_id = UserCreate.key

            UserRole.put()
        return redirect(url_for('Home'))

    return render_template('user/edit-super-admin.html', **locals())


@app.route('/recording/user')
@login_required
@roles_required(('super_admin', 'manager_agency'))
def User_Index():
    menu='recording'
    submenu='user'

    admin_role = RoleModel.query(
        RoleModel.name == 'admin'
    ).get()

    super_admin_role = RoleModel.query(
        RoleModel.name == 'super_admin'
    ).get()

    user_admin = []
    if admin_role:
        user_admin = UserRoleModel.query(
            ndb.OR(
                UserRoleModel.role_id == super_admin_role.key,
                UserRoleModel.role_id == admin_role.key
            )
        )

    user_admins = [users.user_id for users in user_admin]

    user = UserRoleModel.query(
        projection=[UserRoleModel.user_id],
        group_by=[UserRoleModel.user_id]
    )

    return render_template('/user/index-user.html', **locals())

