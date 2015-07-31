__author__ = 'Wilrona'


from ...modules import *
from model_config import ConfigModel, SynchroModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route('/synchronization')
def synchronization():
    token = request.args.get('token')

    url_config = ConfigModel.query(
        ConfigModel.token_agency == token
    ).get()

    date_synchro = SynchroModel.query().order(-SynchroModel.date).get()

    vessel = vessel_api(url_config.url_server, token, "/vessel/get/", date_synchro)

    return redirect(url_for('Home'))


def vessel_api(url, tocken, segment, date):
    from ..vessel.models_vessel import VesselModel


    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))

    for data_get in result['vessel']:
        old_data = VesselModel.get_by_id(data_get['vessel_id'])
        if old_data:
            old_data.name = data_get['vessel_name']
            old_data.capacity = data_get['vessel_capacity']
            old_data.immatricul = data_get['vessel_immatricul']
            old_data.put()
        else:
            data_save = VesselModel(id=data_get['vessel_id'])
            data_save.name = data_get['vessel_name']
            data_save.capacity = data_get['vessel_capacity']
            data_save.immatricul = data_get['vessel_immatricul']
            data_save.put()


def currency_api(url, tocken, segment, date):
    from ..currency.models_currency import CurrencyModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))

    for data_get in result['currency']:
        old_data = CurrencyModel.get_by_id(data_get['currency_id'])
        if old_data:
            old_data.name = data_get['currency_name']
            old_data.code = data_get['currency_code']
            old_data.put()
        else:
            data_save = CurrencyModel(id=data_get['currency_id'])
            data_save.name = data_get['currency_name']
            data_save.code = data_get['currency_code']
            data_save.put()


def destination_api(url, tocken, segment, date):
    from ..destination.models_destination import DestinationModel, CurrencyModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))

    for data_get in result['destination']:
        old_data = DestinationModel.get_by_id(data_get['destination_id'])
        if old_data:
            old_data.name = data_get['destination_name']
            old_data.code = data_get['destination_code']

            local_currency = CurrencyModel.get_by_id(data_get['destination_currency']['currency_id'])
            old_data.currency = local_currency.key

            old_data.put()
        else:
            data_save = DestinationModel(id=data_get['destination_id'])
            data_save.name = data_get['destination_name']
            data_save.code = data_get['destination_code']

            local_currency = CurrencyModel.get_by_id(data_get['destination_currency']['currency_id'])
            data_save.currency = local_currency.key

            data_save.put()


def travel_line_api(url, tocken, segment, date):
    from ..travel.models_travel import TravelModel, DestinationModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))

    for data_get in result['travel']:
        old_data = TravelModel.get_by_id(data_get['travel_id'])
        if old_data:
            old_data.time = function.time_convert(data_get['travel_time'])

            local_start = DestinationModel.get_by_id(data_get['travel_start'])
            old_data.destination_start = local_start.key

            local_check = DestinationModel.get_by_id(data_get['travel_check'])
            old_data.destination_check = local_check.key
            old_data.put()
        else:
            data_save = TravelModel(id=data_get['travel_id'])
            data_save.time = function.time_convert(data_get['travel_time'])

            local_start = DestinationModel.get_by_id(data_get['travel_start'])
            old_data.destination_start = local_start.key

            local_check = DestinationModel.get_by_id(data_get['travel_check'])
            old_data.destination_check = local_check.key

            data_save.put()


def agency_api(url, tocken, segment, date):
    from ..agency.models_agency import AgencyModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))

    if result['agency']:
        old_data = AgencyModel.get_by_id(result['agency']['agency_id'])
        old_data.name = result['agency']['agency_name']
        old_data.country = result['agency']['agency_country']
        old_data.phone = result['agency']['agency_phone']
        old_data.fax = result['agency']['agency_fax']
        old_data.adress = result['agency']['agency_adress']
        old_data.reduction = result['agency']['agency_reduction']
        old_data.status = result['agency']['agency_status']
        old_data.is_achouka = result['agency']['agency_is_achouka']
        old_data.put()


def role_api(url, tocken, segment, date):
    from ..user.models_user import RoleModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))

    for data_get in result['role']:
        old_data = RoleModel.get_by_id(data_get['role_id'])
        if old_data:
            old_data.visible = data_get['role_visible']
            old_data.name = data_get['role_name']
            old_data.put()
        else:
            data_save = RoleModel(id=data_get['role_id'])
            data_save.visible = data_get['role_visible']
            data_save.name = data_get['role_name']
            data_save.put()


def profil_api(url, tocken, segment, date):
    from ..user.models_user import ProfilRoleModel, RoleModel, ProfilModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))

    for data_get in result['profils']:
        old_data = ProfilModel.get_by_id(data_get['profil_id'])
        if old_data:
            old_data.standard = data_get['profil_standard']
            old_data.enable = data_get['profil_enable']
            old_data.name = data_get['profil_name']

            #suppression de toutes les relations profils et roles
            profil_role_delete = ProfilRoleModel.query(
                ProfilRoleModel.profil_id == old_data.key
            )
            for role_delete in profil_role_delete:
                role_delete.key.delete()

            for data_child_get in data_get['profil_roles']:
                old_child_data = RoleModel.get_by_id(data_child_get['role_id'])
                if old_child_data:
                    profil_role = ProfilRoleModel()
                    profil_role.profil_id = old_data.key
                    profil_role.role_id = old_child_data.key
                    profil_role.put()

            old_data.put()
        else:
            data_save = ProfilModel(id=data_get['profil_id'])
            data_save.standard = data_get['profil_standard']
            data_save.enable = data_get['profil_enable']
            data_save.name = data_get['profil_name']
            save = data_save.put()
            for data_child_get in data_get['profil_roles']:
                old_child_data = RoleModel.get_by_id(data_child_get['role_id'])
                if old_child_data:
                    profil_role = ProfilRoleModel()
                    profil_role.profil_id = save
                    profil_role.role_id = old_child_data.key
                    profil_role.put()


def user_api(url, tocken, segment, date):
    from ..user.models_user import UserModel, AgencyModel, ProfilModel, ProfilRoleModel, UserRoleModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))

    for data_get in result['user']:
        old_data = UserModel.get_by_id(data_get['user_id'])
        if old_data:
            old_data.password = data_get['password']
            old_data.email = data_get['email']
            old_data.first_name = data_get['first_name']
            old_data.last_name = data_get['last_name']
            old_data.phone = data_get['phone']
            old_data.dial_code = data_get['dial_code']
            old_data.enabled = data_get['enabled']

            agency_user = AgencyModel.get_by_id(data_get['agency_id'])
            old_data.agency = agency_user.key

            profil_user = ProfilModel.get_by_id(data_get['profil_id'])
            old_data.profil = profil_user.key

            profil_role_user = ProfilRoleModel.query(
                ProfilRoleModel.profil_id == profil_user.key
            )

            #suppression de toutes les relations profils et roles
            user_role_delete = UserRoleModel.query(
                UserRoleModel.user_id == old_data.key
            )
            for role_delete in user_role_delete:
                role_delete.key.delete()

            for role in profil_role_user:
                user_role = UserRoleModel()
                user_role.user_id = old_data.key
                user_role.role_id = role.key
                user_role.put()

            old_data.put()
        else:
            data_save = UserModel(id=data_get['user_id'])
            data_save.password = data_get['password']
            data_save.email = data_get['email']
            data_save.first_name = data_get['first_name']
            data_save.last_name = data_get['last_name']
            data_save.phone = data_get['phone']
            data_save.dial_code = data_get['dial_code']
            data_save.enabled = data_get['enabled']

            agency_user = AgencyModel.get_by_id(data_get['agency_id'])
            data_save.agency = agency_user.key

            profil_user = ProfilModel.get_by_id(data_get['profil_id'])
            data_save.profil = profil_user.key

            profil_role_user = ProfilRoleModel.query(
                ProfilRoleModel.profil_id == profil_user.key
            )

            for role in profil_role_user:
                user_role = UserRoleModel()
                user_role.user_id = old_data.key
                user_role.role_id = role.key
                user_role.put()

            data_save.put()