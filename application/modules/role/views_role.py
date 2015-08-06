__author__ = 'wilrona'

from ...modules import *

from ..user.models_user import RoleModel

from forms_role import FormRole


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route('/settings/role', methods=['GET', 'POST'])
@app.route('/settings/role/<int:role_id>', methods=['GET', 'POST'])
def Role_Index(role_id=None):
    menu = 'settings'
    submenu = 'role'

    if role_id:
        role = RoleModel.get_by_id(role_id)
        form = FormRole(obj=role)
    else:
        form = FormRole(request.form)
        role = RoleModel()

    if form.validate_on_submit():
        role_exis = RoleModel.query(RoleModel.name == form.name.data).count()
        if role_exis >= 1:
            form.name.errors.append('This name '+str(form.name.data)+' exist')
        else:
            role.name = form.name.data
            try:
                role.put()
                flash(u' Role Save. ', 'success')
                return redirect(url_for('Role_Index'))
            except CapabilityDisabledError:
                flash(u' Error data base. ', 'danger')
                return redirect(url_for('Role_Index'))

    role_list = RoleModel.query()

    return render_template('/role/index.html', **locals())


@app.route('/Generate_Role')
def Generate_Role():
    number = 0
    for k, v in global_role.items():
        role_present = RoleModel.query(
            RoleModel.name == k
        ).get()
        if not role_present:
            role = RoleModel()
            role.name = k
            role.visible = v
            role.put()
            number += 1


    flash(u' All Role generated. (' + str(number) +u')', 'success')
    return redirect(url_for('Role_Index'))


@app.route('/Active_Role/<int:role_id>')
def Active_Role(role_id):

    role = RoleModel.get_by_id(role_id)

    if not role_id:
        flash(u' Profil is not correct. ', 'danger')
        return redirect(url_for('Role_Index'))

    if role.visible:
        role.visible = False
    else:
        role.visible = True

    role.put()
    flash(u' Role Updated. ', 'success')
    return redirect(url_for('Role_Index'))
