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


@app.route('/settings/user/admin')
@login_required
@roles_required(('super_admin', 'admin'))
def User_Admin_Index():
    menu='settings'
    submenu ='user_admin'

    admin_role = RoleModel.query(
        RoleModel.name == 'admin'
    ).get()

    user_admin = []
    if admin_role:
        user_admin = UserRoleModel.query(
                UserRoleModel.role_id == admin_role.key
        )

    if current_user.has_roles('super_admin'):
        super_admin_role = RoleModel.query(
            RoleModel.name == 'super_admin'
        ).get()

        super_admin_role_id = UserRoleModel.query(
            UserRoleModel.role_id == super_admin_role.key
        )
        super_admin_id = [users.user_id for users in super_admin_role_id]

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

    return render_template('/user/index.html', **locals())


@app.route('/settings/user/admin/edit', methods=['GET', 'POST'])
@app.route('/settings/user/admin/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('super_admin', 'admin'))
def User_Admin_Edit(user_id=None):
    menu='settings'
    submenu ='user_admin'

    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")
    
    number_list = global_dial_code_custom

    # recuperation du role admin
    role = RoleModel.query(
            RoleModel.name == 'admin'
    ).get()

    if not role:
        flash('you do not create admin role', 'danger')
        return redirect(url_for('User_Admin_Index'))

    #liste des devises pour les administrateurs
    currency = CurrencyModel.query()

    #liste des agences dans l'application
    agency = AgencyModel.query(
        AgencyModel.is_achouka == True
    )

    if user_id:
        User = UserModel.get_by_id(user_id)
        form = FormEditUserAdmin(obj=User)
    else:
        form = FormRegisterUserAdmin(request.form)
        User = UserModel()

    activity = ActivityModel()
    activity.user_modify = current_user.key
    activity.object = "UserModel"
    activity.time = function.datetime_convert(date_auto_nows)

    if form.validate_on_submit():

        ProfilRole = ProfilRoleModel.query(
            ProfilRoleModel.role_id == role.key
        ).count()

        if ProfilRole == 1:
            profil = ProfilRoleModel.query(
                ProfilRoleModel.role_id == role.key
            ).get()

            currency = CurrencyModel.get_by_id(int(form.currency.data))

            User.first_name = form.first_name.data
            User.last_name = form.last_name.data

            User.phone = form.phone.data
            User.dial_code = form.dial_code.data
            User.currency = currency.key

            User.agency = None



            if not user_id:
                User.email = form.email.data
                password = hashlib.sha224(form.password.data).hexdigest()
                User.password = password

            UserCreate = User.put()

            if not user_id:
                #recuperation de chaque role appartenant au profil ayant le role admin
                all_role = ProfilRoleModel.query(
                    ProfilRoleModel.profil_id == profil.profil_id
                )

                # insertion de chaque role a l'utilisateur cree
                UserCreate = UserModel.get_by_id(UserCreate.id())

                for role in all_role:

                    UserRole = UserRoleModel()

                    UserRole.role_id = role.role_id
                    UserRole.user_id = UserCreate.key
                    UserRole.put()

                UserCreate.profil = profil.profil_id #profil pour les comptes admins
                UserCreate.put()

            if user_id:
                activity.identity = user_id
                activity.nature = 4
                activity.put()
                flash('User Updated', 'success')

            else:
                activity.identity = UserCreate.key.id()
                activity.nature = 1
                activity.put()
                flash('User Created', 'success')

            return redirect(url_for('User_Admin_Index'))

        else:
            flash('Create before profil admin with role "Admin" for this user or you have two profil have a role "Admin"', 'danger')

    return render_template('/user/edit.html', **locals())
    
#-------------------------------------------------------------------------------
# activation et desactivation du compte admin
#-------------------------------------------------------------------------------

@app.route('/setting/user/status/<int:user_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('super_admin', 'admin'))
def activate_user_admin(user_id=None):
    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    activity = ActivityModel()
    activity.user_modify = current_user.key
    activity.object = "UserModel"
    activity.time = function.datetime_convert(date_auto_nows)

    user_status = UserModel.get_by_id(user_id)

    if user_status.is_enabled:
        user_status.is_enabled = False
        activity.nature = 2
    else:
        user_status.is_enabled = True
        activity.nature = 5

    user_status.put()

    activity.identity = user_status.key.id()
    activity.put()

    flash(u'Admin is activated!', 'success')
    return redirect(url_for("User_Admin_Index"))


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



@app.route('/recording/user/edit', methods=['GET', 'POST'])
@app.route('/recording/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('super_admin', 'manager_agency'))
def User_Edit(user_id=None):
    menu = 'recording'
    submenu = 'user'

    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    activity = ActivityModel()
    activity.user_modify = current_user.key
    activity.object = "UserModel"
    activity.time = function.datetime_convert(date_auto_nows)
    
    number_list = global_dial_code_custom

    # recuperation du role admin
    role = RoleModel.query(
        RoleModel.name == 'admin'
    ).get()

    profil_admin = ProfilRoleModel.query(
        ProfilRoleModel.role_id == role.key
    ).get()

    if not profil_admin:
        flash('you do not create admin profiles', 'danger')
        return redirect(url_for('User_Index'))

    profils = ProfilRoleModel.query(
        ProfilRoleModel.profil_id != profil_admin.profil_id,
        projection=[ProfilRoleModel.profil_id],
        group_by=[ProfilRoleModel.profil_id]
    )

    #liste des agences dans l'application
    agency = AgencyModel.query(
        AgencyModel.is_achouka == True
    )

    if user_id:
        User = UserModel.get_by_id(user_id)
        form = FormEditUser(obj=User)
    else:
        form = FormRegisterUser(request.form)
        User = UserModel()

    if form.validate_on_submit():

        profil = ProfilModel.get_by_id(int(form.profil.data))
        agency = AgencyModel.get_by_id(int(form.agency.data))

        # supprimer les roles lors de la modification du profil
        if User.profil and User.profil != profil.key and user_id:
            role_del = ProfilRoleModel.query(
                ProfilRoleModel.profil_id == User.profil
            )

            for role_del in role_del:
                remove_role = UserRoleModel.query(
                    UserRoleModel.role_id == role_del.role_id,
                    UserRoleModel.user_id == User.key
                ).get()

                remove_role.key.delete()

        User.first_name = form.first_name.data
        User.last_name = form.last_name.data

        User.phone = form.phone.data
        User.dial_code = form.dial_code.data
        User.profil = profil.key

        if agency:
            User.agency = agency.key

        if not user_id:
            User.email = form.email.data
            password = hashlib.sha224(form.password.data).hexdigest()
            User.password = password

        UserCreate = User.put()

        #recuperation de chaque role appartenant au profil choisie
        all_role = ProfilRoleModel.query(
            ProfilRoleModel.profil_id == profil.key
        )

        # insertion de chaque role a l'utilisateur cree
        this_user = UserCreate = UserModel.get_by_id(UserCreate.id())

        for role in all_role:

            UserRole = UserRoleModel()

            UserRole.role_id = role.role_id
            UserRole.user_id = UserCreate.key
            UserRole.put()

        if user_id:
            activity.identity = user_id
            activity.nature = 4
            activity.put()
            flash('User Updated', 'success')
        else:
            activity.identity = this_user.key.id()
            activity.nature = 1
            activity.put()
            flash('User Created', 'success')

        return redirect(url_for('User_Index'))

    return render_template('/user/edit-user.html', **locals())


@app.route('/recording/user/status/<int:user_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Activate_User(user_id=None):
    user_status = UserModel.get_by_id(user_id)

    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    activity = ActivityModel()
    activity.user_modify = current_user.key
    activity.object = "UserModel"
    activity.time = function.datetime_convert(date_auto_nows)

    if user_status.is_enabled:
        activity.identity = user_status.key.id()
        activity.nature = 2
        activity.put()
        flash(u'User is disabled!', 'success')
        user_status.is_enabled = False
    else:
        activity.identity = user_status.key.id()
        activity.nature = 5
        activity.put()
        flash(u'User is activated!', 'success')
        user_status.is_enabled = True

    user_status.put()

    return redirect(url_for("User_Index"))
