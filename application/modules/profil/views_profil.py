__author__ = 'wilrona'

from ...modules import *

from models_profil import ProfilModel
from forms_profil import FormProfil

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route('/settings/profil')
@login_required
@roles_required(('admin', 'super_admin'))
def Profil_Index():
    menu = 'settings'
    submenu = 'profil'

    profil_lists = ProfilModel.query()

    from ..user.models_user import ProfilRoleModel, RoleModel

    from ..activity.models_activity import ActivityModel
    feed = ActivityModel.query(
        ActivityModel.object == 'ProfilModel',
    ).order(
        -ActivityModel.time
    )

    feed_tab = []
    count = 0
    for feed in feed:
        feed_list = {}
        feed_list['user'] = feed.user_modify
        if feed.nature == 10:
            vess = ProfilRoleModel.get_by_id(feed.identity)
            feed_list['data'] = vess.role_id.get().name
            feed_list['last_value'] = vess.profil_id.get().name
            feed_list['id'] = vess.profil_id.get().key.id()
        elif feed.nature == 13:
            vess = RoleModel.get_by_id(feed.identity)
            feed_list['data'] = vess.name
            profiling = ProfilModel.get_by_id(int(feed.last_value))
            feed_list['last_value'] = profiling.name
            feed_list['id'] = profiling.key.id()
        else:
            vess = ProfilModel.get_by_id(feed.identity)
            feed_list['data'] = vess.name
            feed_list['id'] = feed.identity
        feed_list['time'] = feed.time
        feed_list['nature'] = feed.nature
        feed_tab.append(feed_list)
        count += 1
        if count > 5 and not request.args.get('modal'):
            count += 1
            break

    if request.args.get('modal'):
        return render_template('/profil/all_feed.html', **locals())

    return render_template('/profil/index.html', **locals())


@app.route('/settings/profil/view/<int:profil_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('admin', 'super_admin'))
def Profil_View(profil_id):
    menu = 'settings'
    submenu = 'profil'
    from ..user.models_user import ProfilRoleModel

    profil = ProfilModel.get_by_id(profil_id)
    form = FormProfil(obj=profil)
    profilRole = ProfilRoleModel.query(ProfilRoleModel.profil_id == profil.key)

    view = True

    return render_template('/profil/edit.html', **locals())


@app.route('/settings/profil/edit', methods=['GET', 'POST'])
@app.route('/settings/profil/edit/<int:profil_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('admin', 'super_admin'))
def Profil_Edit(profil_id=None):
    menu = 'settings'
    submenu = 'profil'
    from ..user.models_user import ProfilRoleModel, RoleModel
    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    feed_tab = []


    if profil_id:
        profil = ProfilModel.get_by_id(profil_id)
        form = FormProfil(obj=profil)
        profilRole = ProfilRoleModel.query(ProfilRoleModel.profil_id == profil.key)

        profilRole_id = [profil_role_id.key.id() for profil_role_id in profilRole]

        feed = ActivityModel.query(
            ActivityModel.object == 'ProfilModel'
        ).order(
            -ActivityModel.time
        )
        count = 0
        for feed in feed:
            feed_list = {}
            feed_list['user'] = feed.user_modify
            if feed.identity == profil.key.id(): #AFFICHER TOUTES LES MODIFICATIONS EFFECTUE SUR LE PROFIL
                vess = ProfilModel.get_by_id(feed.identity)
                feed_list['data'] = vess.name
                feed_list['id'] = feed.identity
                feed_list['time'] = feed.time
                feed_list['nature'] = feed.nature
                feed_tab.append(feed_list)

            if feed.identity in profilRole_id: # AFFICHER LES AJOUTS DE ROLE EFFECTUES
                vess = ProfilRoleModel.get_by_id(feed.identity)
                feed_list['data'] = vess.role_id.get().name
                feed_list['last_value'] = vess.profil_id.get().name
                feed_list['id'] = vess.profil_id.get().key.id()
                feed_list['time'] = feed.time
                feed_list['nature'] = feed.nature
                feed_tab.append(feed_list)

            if feed.nature == 13: #AFFICHER LES SUPPRESSIONS EFFECTUEES
                if int(feed.last_value) == profil.key.id():
                    vess = RoleModel.get_by_id(feed.identity)
                    feed_list['data'] = vess.name
                    profiling = ProfilModel.get_by_id(int(feed.last_value))
                    feed_list['last_value'] = profiling.name
                    feed_list['id'] = profiling.key.id()

                    feed_list['time'] = feed.time
                    feed_list['nature'] = feed.nature
                    feed_tab.append(feed_list)
            count += 1
            if count > 5:
                count += 1
                break
    else:
        profil = ProfilModel()
        form = FormProfil(request.form)

    activity = ActivityModel()
    activity.user_modify = current_user.key
    activity.object = "ProfilModel"
    activity.time = function.datetime_convert(date_auto_nows)

    if form.validate_on_submit():
        profil_exist = ProfilModel.query(ProfilModel.name == form.name.data).count()
        if profil_exist >= 1:
            if profil.name == form.name.data:

                profil.name = form.name.data
                if form.standard.data:
                    if int(form.standard.data) == 2:
                        profil.standard = False
                    else:
                        profil.standard = True
                else:
                    profil.standard = False

                this_profil = profil.put()

                activity.identity = this_profil.id()
                activity.nature = 4
                activity.put()

                flash(u' Profil Save. '+str(form.standard.data), 'success')
                return redirect(url_for('Profil_Index'))
            else:
                form.name.errors.append('This name profil '+ str(form.name.data) + 'is already exist')
        else:
            profil.name = form.name.data

            if form.standard.data:
                if int(form.standard.data) == 2:
                    profil.standard = False
                else:
                    profil.standard = True
            else:
                profil.standard = False

            this_profil = profil.put()

            activity.identity = this_profil.id()
            if profil_id:
                activity.nature = 4
            else:
                activity.nature = 1

            activity.put()

            flash(u' Profil Save. ', 'success')
            return redirect(url_for('Profil_Index'))

    return render_template('/profil/edit.html', **locals())


@app.route('/AddRoleProfil/<int:profil_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('admin', 'super_admin'))
def Add_Role_Profil(profil_id):
    from ..user.models_user import ProfilRoleModel, RoleModel
    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    profil_update = ProfilModel.get_by_id(profil_id)

    profilrole = ProfilRoleModel.query(
        ProfilRoleModel.profil_id == profil_update.key
    )

    profilrole = [role.role_id for role in profilrole]

    if current_user.has_roles('super_admin'):
        roles = RoleModel.query()
    else:
        roles = RoleModel.query(
            RoleModel.visible == True
        )

    if request.method == "POST":
        post_role = request.form.getlist('roles')
        nombre = 0
        for role in post_role:
            slc_role = RoleModel.get_by_id(int(role))
            if slc_role:
                profilRole = ProfilRoleModel()
                profilRole.role_id = slc_role.key
                profilRole.profil_id = profil_update.key
                this_role_profil = profilRole.put()

                activity = ActivityModel()
                activity.user_modify = current_user.key
                activity.object = "ProfilModel"
                activity.time = function.datetime_convert(date_auto_nows)

                activity.identity = this_role_profil.id()
                activity.nature = 10
                activity.put()

            nombre += 1

        if nombre > 0:
            flash('you have add '+str(nombre)+' Role for this profil', 'success')
        else:
            flash('you have add '+str(nombre)+' Role for this profil', 'danger')
        # Mise a jour de la date de modification du profil
        profil_update.put()
        return redirect(url_for('Profil_Edit', profil_id=profil_id))

    return render_template('/profil/list_role.html', **locals())



@app.route('/DeleteRoleProfil/<int:profilrole_id>/<int:profil_id>')
@login_required
@roles_required(('admin', 'super_admin'))
def Delete_Role_Profil(profilrole_id, profil_id):
    from ..user.models_user import ProfilRoleModel
    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    profilrole = ProfilRoleModel.get_by_id(profilrole_id)
    profil = ProfilModel.get_by_id(profil_id)

    del_activity = ActivityModel.query(
            ActivityModel.object == "ProfilModel",
            ActivityModel.identity == profilrole.key.id()
    )

    for del_act in del_activity:
        del_act.key.delete()

    activity = ActivityModel()
    activity.user_modify = current_user.key
    activity.object = "ProfilModel"
    activity.time = function.datetime_convert(date_auto_nows)

    if profilrole:
        activity.identity = profilrole.role_id.get().key.id()
        activity.nature = 13
        activity.last_value = str(profilrole.profil_id.get().key.id())
        activity.put()

        profilrole.key.delete()
        flash('Role Deleted', 'success')
    else:
        flash('Data not found', 'danger')

    # Mise a jout de profil
    profil.put()
    return redirect(url_for('Profil_Edit', profil_id=profil.key.id()))


@app.route('/settings/profil/delete/<int:profil_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('admin', 'super_admin'))
def Profil_Delete(profil_id):
    """ Suppression des profils """
    from ..user.models_user import ProfilRoleModel, UserModel
    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    activity = ActivityModel()
    activity.user_modify = current_user.key
    activity.object = "ProfilModel"
    activity.time = function.datetime_convert(date_auto_nows)

    delete_profil = ProfilModel.get_by_id(profil_id)

    role_profil_exist = ProfilRoleModel.query(
        ProfilRoleModel.profil_id == delete_profil.key
    ).count()

    user_profil_exist = UserModel.query(
        UserModel.profil == delete_profil.key
    ).count()

    if role_profil_exist >= 1 or user_profil_exist >= 1:
        flash(u'You can\'t delete this profil', 'danger')
        return redirect(url_for("Profil_Index"))
    else:
        activity.identity = delete_profil.key.id()
        activity.nature = 3
        activity.put()

        delete_profil.key.delete()
        flash(u'Profil has been deleted successfully', 'success')
        return redirect(url_for("Profil_Index"))

