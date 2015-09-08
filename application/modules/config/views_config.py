__author__ = 'Wilrona'


from ...modules import *
from model_config import ConfigModel, SynchroModel, AgencyModel
from clean_bd import *

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route('/synchronization')
def synchronization():
    token = request.args.get('token')

    url_config = ConfigModel.query(
            ConfigModel.token_agency == token
    ).get()

    if token:
        date_synchro = SynchroModel.query(
            SynchroModel.agency_synchro == url_config.local_ref
        ).order(-SynchroModel.date).get()
    else:
        active_agency = AgencyModel.query(
            AgencyModel.local_status == True
        ).get()

        date_synchro = SynchroModel.query(
            SynchroModel.agency_synchro == active_agency.key
        ).order(-SynchroModel.date).get()

    if date_synchro:
        date = date_synchro.date

        if not date_synchro.time_departure:
            date_combine_departure = datetime.datetime.combine(date, date_synchro.time_all)
        else:
            date_combine_departure = datetime.datetime.combine(date, date_synchro.time_departure)

        if not date_synchro.time_customer:
            date_combine_customer = datetime.datetime.combine(date, date_synchro.time_all)
        else:
            date_combine_customer = datetime.datetime.combine(date, date_synchro.time_customer)

        if not date_synchro.time_customer_put:
            date_customer_put = date_synchro.time_all
        else:
            date_customer_put = date_synchro.time_customer_put

        if not date_synchro.time_ticket_sale_put:
            date_ticket_sale = date_synchro.time_all
        else:
            date_ticket_sale = date_synchro.time_ticket_sale_put

        if not date_synchro.time_ticket_sale_online:
            date_sale_online = date_synchro.time_all
        else:
            date_sale_online = date_synchro.time_ticket_sale_online

        if not date_synchro.time_return_and_doublons_foreign:
            date_return_doublons = date_synchro.time_all
        else:
            date_return_doublons = date_synchro.time_return_and_doublons_foreign

    else:
        date = None
        date_combine_departure = None
        date_combine_customer = None
        date_customer_put = None
        date_ticket_sale = None
        date_sale_online = None
        date_return_doublons = None

    # ajout des informations
    data_vessel = vessel_api(url_config.url_server, token, "/vessel/get/", date)
    data_currency = currency_api(url_config.url_server, token, "/currency/get/", date)
    data_destination = destination_api(url_config.url_server, token, "/destination/get/", date)
    travel_line_api(url_config.url_server, token, "/travel/get/", date)
    agency_api(url_config.url_server, token, "/agency/get/", date)
    role_api(url_config.url_server, token, "/role/get/", date)
    profil_api(url_config.url_server, token, "/profil/get/", date)
    user_api(url_config.url_server, token, "/user/get/", date)

    departure_api(url_config.url_server, token, "/departure/get/", date_combine_departure)

    data_class = class_api(url_config.url_server, token, "/class/get/", date)
    data_journey = journey_api(url_config.url_server, token, "/journey/get/", date)
    data_category = category_api(url_config.url_server, token, "/category/get/", date)
    tickettype_api(url_config.url_server, token, "/tickets/get/", date)

    customer_api(url_config.url_server, token, "/customer/get/", date_combine_customer)

    if date:
        customer_api_put(url_config.url_server, token, "/customer/put/", date_customer_put)
        ticket_sale_put_api(url_config.url_server, token, "/ticket_local_sale_put/put/", date_ticket_sale)

    # Insertion des tickets alloues
    ticket_allocated_api(url_config.url_server, token, "/tickets_allocated/get/", date)
    get_ticket_sale_online(url_config.url_server, token, "/get_ticket_online/get/", date_sale_online)
    get_doublons_ticket_return_api(url_config.url_server, token, "/tickets_doublons_ticket_return_sale/get/", date_return_doublons)

    set_status_ticket_put()

    # Netoyage de la base de donnee
    clean_vessel(data_vessel)
    clean_currency(data_currency)
    clean_destination(data_destination)
    clean_class(data_class)
    clean_journey(data_journey)
    clean_categpry(data_category)
    clean_ticket()

    if date_synchro:
        date_synchro.time_all = datetime.datetime.now().time()
        date_synchro.put()
    else:
        Synchro = SynchroModel()
        Synchro.agency_synchro = url_config.local_ref
        Synchro.put()

    if token:
        flash('Success Synchronization', 'success')
        return redirect(url_for('Home'))
    else:
        return "true"


@app.route('/add_agency', methods=['POST'])
def add_agency():
    from ..agency.models_agency import AgencyModel, DestinationModel

    token = request.form['token']
    if not token:
        flash("token empty", "danger")
        return redirect(url_for('Dashboard'))

    local_active_agency = AgencyModel.query(
        AgencyModel.local_status == True
    ).get()

    url_config = ConfigModel.query(
        ConfigModel.local_ref == local_active_agency.key
    ).get()

    url = ""+url_config.url_server+"/agency/get/"+token
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
    else:
        if result['agency']:
            old_data = AgencyModel.get_by_id(result['agency']['agency_id'])

            agency_new = None

            if not old_data:
                new_data = AgencyModel(id=result['agency']['agency_id'])
                new_data.name = result['agency']['agency_name']
                new_data.country = result['agency']['agency_country']
                new_data.phone = result['agency']['agency_phone']
                new_data.fax = result['agency']['agency_fax']
                new_data.address = result['agency']['agency_address']
                new_data.reduction = float(result['agency']['agency_reduction'])
                new_data.status = result['agency']['agency_status']
                new_data.is_achouka = result['agency']['agency_is_achouka']

                destination = DestinationModel.get_by_id(result['agency']['agency_destination'])
                new_data.destination = destination.key

                agency_new = new_data.put()
            else:
                flash("This token exist", "danger")

            if agency_new:
                conf = ConfigModel()
                conf.url_server = url_config.url_server
                conf.local_ref = agency_new
                conf.token_agency = token
                conf.put()

                flash("Agency added", "success")

    return redirect(url_for('Dashboard'))


@app.route('/active_local_agency')
def active_local_agency():

    from ..agency.models_agency import AgencyModel

    agency_id = int(request.args.get("agency_id"))

    agency = AgencyModel.get_by_id(agency_id)

    agency_active = AgencyModel.query(
        AgencyModel.local_status == True
    ).get()
    if agency_active:
        agency_active.local_status = False
        agency_active.put()

    agency.local_status = True
    agency_save = agency.put()

    url_config = ConfigModel.query(
        ConfigModel.local_ref == agency_save
    ).get()

    sychro_agency = SynchroModel.query(
        SynchroModel.agency_synchro == agency_save
    ).order(-SynchroModel.date).get()

    if sychro_agency:
        date = sychro_agency.date

        if not sychro_agency.time_departure:
            date_combine_departure = datetime.datetime.combine(date, sychro_agency.time_all)
        else:
            date_combine_departure = datetime.datetime.combine(date, sychro_agency.time_departure)

        if not sychro_agency.time_customer:
            date_combine_customer = datetime.datetime.combine(date, sychro_agency.time_all)
        else:
            date_combine_customer = datetime.datetime.combine(date, sychro_agency.time_customer)

        if not sychro_agency.time_ticket_sale_online:
            date_sale_online = sychro_agency.time_all
        else:
            date_sale_online = sychro_agency.time_ticket_sale_online

        if not sychro_agency.time_return_and_doublons_foreign:
            date_return_doublons = sychro_agency.time_all
        else:
            date_return_doublons = sychro_agency.time_return_and_doublons_foreign
    else:
        date = None
        date_combine_departure = None
        date_combine_customer = None
        date_sale_online= None
        date_return_doublons = None
    # ajout des informations
    data_vessel = vessel_api(url_config.url_server, url_config.token_agency, "/vessel/get/", date)
    data_currency = currency_api(url_config.url_server, url_config.token_agency, "/currency/get/", date)
    data_destination = destination_api(url_config.url_server, url_config.token_agency, "/destination/get/", date)
    travel_line_api(url_config.url_server, url_config.token_agency, "/travel/get/", date)
    my_agency = agency_api(url_config.url_server, url_config.token_agency, "/agency/get/", date)
    role_api(url_config.url_server, url_config.token_agency, "/role/get/", date)
    profil_api(url_config.url_server, url_config.token_agency, "/profil/get/", date)
    user_api(url_config.url_server, url_config.token_agency, "/user/get/", date)

    departure_api(url_config.url_server, url_config.token_agency, "/departure/get/", date_combine_departure)

    data_class = class_api(url_config.url_server, url_config.token_agency, "/class/get/", date)
    data_journey = journey_api(url_config.url_server, url_config.token_agency, "/journey/get/", date)
    data_category = category_api(url_config.url_server, url_config.token_agency, "/category/get/", date)
    tickettype_api(url_config.url_server, url_config.token_agency, "/tickets/get/", date)

    customer_api(url_config.url_server, url_config.token_agency, "/customer/get/", date_combine_customer)

    # Insertion des tickets alloues
    ticket_allocated_api(url_config.url_server, url_config.token_agency, "/tickets_allocated/get/", date)
    get_ticket_sale_online(url_config.url_server, url_config.token_agency, "/get_ticket_online/get/", date_sale_online)
    get_doublons_ticket_return_api(url_config.url_server, url_config.token_agency, "/tickets_doublons_ticket_return_sale/get/", date_return_doublons)

    # Netoyage de la base de donnee
    clean_vessel(data_vessel)
    clean_currency(data_currency)
    clean_destination(data_destination)
    clean_class(data_class)
    clean_journey(data_journey)
    clean_categpry(data_category)
    clean_ticket()

    if sychro_agency:
        sychro_agency.time_all = datetime.datetime.now().time()
        sychro_agency.put()
    else:
        Synchro = SynchroModel()
        Synchro.agency_synchro = url_config.local_ref
        Synchro.put()

    flash("Agency activated : "+agency.name, "success")
    return redirect(url_for('Dashboard'))


def vessel_api(url, tocken, segment, date=None):
    from ..vessel.models_vessel import VesselModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    _ids = []
    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))
    else:
        for data_get in result['vessel']:
            old_data = VesselModel.get_by_id(data_get['vessel_id'])
            if old_data:
                old_data.name = data_get['vessel_name']
                old_data.capacity = data_get['vessel_capacity']
                old_data.immatricul = data_get['vessel_immatricul']
                data = old_data.put()
            else:
                data_save = VesselModel(id=data_get['vessel_id'])
                data_save.name = data_get['vessel_name']
                data_save.capacity = data_get['vessel_capacity']
                data_save.immatricul = data_get['vessel_immatricul']
                data = data_save.put()
            _ids.append(data.id())
    return _ids


def currency_api(url, tocken, segment, date=None):
    from ..currency.models_currency import CurrencyModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    _ids = []
    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))
    else:
        for data_get in result['currency']:
            old_data = CurrencyModel.get_by_id(data_get['currency_id'])
            if old_data:
                old_data.name = data_get['currency_name']
                old_data.code = data_get['currency_code']
                data = old_data.put()
            else:
                data_save = CurrencyModel(id=data_get['currency_id'])
                data_save.name = data_get['currency_name']
                data_save.code = data_get['currency_code']
                data = data_save.put()
            _ids.append(data.id())
    return _ids


def destination_api(url, tocken, segment, date=None):
    from ..destination.models_destination import DestinationModel, CurrencyModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    _ids = []
    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))
    else:
        for data_get in result['destination']:
            old_data = DestinationModel.get_by_id(data_get['destination_id'])
            if old_data:
                old_data.name = data_get['destination_name']
                old_data.code = data_get['destination_code']

                local_currency = CurrencyModel.get_by_id(data_get['destination_currency']['currency_id'])
                old_data.currency = local_currency.key

                data = old_data.put()
            else:
                data_save = DestinationModel(id=data_get['destination_id'])
                data_save.name = data_get['destination_name']
                data_save.code = data_get['destination_code']

                local_currency = CurrencyModel.get_by_id(data_get['destination_currency']['currency_id'])
                data_save.currency = local_currency.key

                data = data_save.put()
            _ids.append(data.id())
    return _ids


def travel_line_api(url, tocken, segment, date=None):
    from ..travel.models_travel import TravelModel, DestinationModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))
    else:
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
                data_save.destination_start = local_start.key

                local_check = DestinationModel.get_by_id(data_get['travel_check'])
                data_save.destination_check = local_check.key

                data_save.put()



def agency_api(url, tocken, segment, date=None):
    from ..agency.models_agency import AgencyModel, DestinationModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))
    else:
        if result['agency']:
            old_data = AgencyModel.get_by_id(result['agency']['agency_id'])
            old_data.name = result['agency']['agency_name']
            old_data.country = result['agency']['agency_country']
            old_data.phone = result['agency']['agency_phone']
            old_data.fax = result['agency']['agency_fax']
            old_data.address = result['agency']['agency_address']
            old_data.reduction = float(result['agency']['agency_reduction'])
            old_data.status = result['agency']['agency_status']
            old_data.is_achouka = result['agency']['agency_is_achouka']

            destination = DestinationModel.get_by_id(result['agency']['agency_destination'])
            old_data.destination = destination.key

            agency = old_data.put()

            return agency




def role_api(url, tocken, segment, date=None):
    from ..user.models_user import RoleModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))
    else:
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


def profil_api(url, tocken, segment, date=None):
    from ..user.models_user import ProfilRoleModel, RoleModel, ProfilModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))
    else:
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


def user_api(url, tocken, segment, date=None):
    from ..user.models_user import UserModel, AgencyModel, ProfilModel, ProfilRoleModel, UserRoleModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))
    else:
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
                    user_role.role_id = role.role_id
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
                    user_role.user_id = data_save.key
                    user_role.role_id = role.role_id
                    user_role.put()

                data_save.put()


def departure_api(url, tocken, segment, date=None):
    from ..departure.models_departure import DepartureModel, TravelModel, VesselModel
    from ..config.model_config import SynchroModel, AgencyModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))
    else:
        for data_get in result['departure']:
            old_data = DepartureModel.get_by_id(data_get['departure_id'])
            if old_data:
                old_data.departure_date = function.date_convert(data_get['departure_date'])
                old_data.schedule = function.time_convert(data_get['departure_schedule'])

                if data_get['delay']:
                    old_data.time_delay = function.time_convert(data_get['departure_delay'])

                travel_departure = TravelModel.get_by_id(data_get['departure_destination'])
                old_data.destination = travel_departure.key

                vessel_departure = VesselModel.get_by_id(data_get['departure_vessel'])
                old_data.vessel = vessel_departure.key
                old_data.put()
            else:
                data_save = DepartureModel(id=data_get['departure_id'])

                data_save.departure_date = function.date_convert(data_get['departure_date'])
                data_save.schedule = function.time_convert(data_get['departure_schedule'])

                if data_get['delay']:
                    data_save.time_delay = function.time_convert(data_get['departure_delay'])

                travel_departure = TravelModel.get_by_id(data_get['departure_destination'])
                data_save.destination = travel_departure.key

                vessel_departure = VesselModel.get_by_id(data_get['departure_vessel'])
                data_save.vessel = vessel_departure.key

                data_save.put()

        active_agency = AgencyModel.query(
            AgencyModel.local_status == True
        ).get()

        date_synchro = SynchroModel.query(
            SynchroModel.agency_synchro == active_agency.key
        ).order(-SynchroModel.date).get()

        date_synchro.time_departure = datetime.datetime.now().time()
        date_synchro.put()


def class_api(url, tocken, segment, date=None):
    from ..ticket_type.models_ticket_type import ClassTypeModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    _ids = []
    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))
    else:
        for data_get in result['class']:
            old_data = ClassTypeModel.get_by_id(data_get['class_id'])
            if old_data:
                old_data.default = data_get['class_default']
                old_data.name = data_get['class_name']
                data = old_data.put()
            else:
                data_save = ClassTypeModel(id=data_get['class_id'])
                data_save.default = data_get['class_default']
                data_save.name = data_get['class_name']
                data = data_save.put()
            _ids.append(data.id())
    return _ids

def category_api(url, tocken, segment, date=None):
    from ..ticket_type.models_ticket_type import TicketTypeNameModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    _ids = []
    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))
    else:
        for data_get in result['category']:
            old_data = TicketTypeNameModel.get_by_id(data_get['category_id'])
            if old_data:
                old_data.is_child = data_get['category_is_child']
                old_data.default = data_get['category_default']
                old_data.special = data_get['category_special']
                old_data.name = data_get['category_name']
                data = old_data.put()
            else:
                data_save = TicketTypeNameModel(id=data_get['category_id'])
                data_save.is_child = data_get['category_is_child']
                data_save.default = data_get['category_default']
                data_save.special = data_get['category_special']
                data_save.name = data_get['category_name']
                data = data_save.put()
            _ids.append(data.id())
    return _ids

def journey_api(url, tocken, segment, date=None):
    from ..ticket_type.models_ticket_type import JourneyTypeModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    _ids = []
    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))
    else:
        for data_get in result['journey']:
            old_data = JourneyTypeModel.get_by_id(data_get['journey_id'])
            if old_data:
                old_data.returned = data_get['journey_returned']
                old_data.default = data_get['journey_default']
                old_data.name = data_get['journey_name']
                data = old_data.put()
            else:
                data_save = JourneyTypeModel(id=data_get['journey_id'])
                data_save.returned = data_get['journey_returned']
                data_save.default = data_get['journey_default']
                data_save.name = data_get['journey_name']
                data = data_save.put()
            _ids.append(data.id())
    return _ids


def tickettype_api(url, tocken, segment, date=None):
    from ..ticket_type.models_ticket_type import TicketTypeModel, ClassTypeModel, CurrencyModel, JourneyTypeModel, TicketTypeNameModel, TravelModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    _ids = []
    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))
    else:
        for data_get in result['tickets']:
            old_data = TicketTypeModel.get_by_id(data_get['ticket_id'])
            if old_data:
                old_data.name = data_get['ticket_name']
                old_data.price = data_get['ticket_price']
                old_data.active = data_get['ticket_active']

                type_name = TicketTypeNameModel.get_by_id(data_get['ticket_type_name'])
                old_data.type_name = type_name.key

                journey_name = JourneyTypeModel.get_by_id(data_get['ticket_journey_name'])
                old_data.journey_name = journey_name.key

                class_name = ClassTypeModel.get_by_id(data_get['ticket_class_name'])
                old_data.class_name = class_name.key


                currency_ticket = CurrencyModel.get_by_id(data_get['ticket_currency'])
                old_data.currency = currency_ticket.key

                travel_ticket = TravelModel.get_by_id(data_get['ticket_travel'])
                old_data.travel = travel_ticket.key

                data = old_data.put()
            else:
                data_save = TicketTypeModel(id=data_get['ticket_id'])

                data_save.name = data_get['ticket_name']
                data_save.price = data_get['ticket_price']
                data_save.active = data_get['ticket_active']

                type_name = TicketTypeNameModel.get_by_id(data_get['ticket_type_name'])
                data_save.type_name = type_name.key

                journey_name = JourneyTypeModel.get_by_id(data_get['ticket_journey_name'])
                data_save.journey_name = journey_name.key

                class_name = ClassTypeModel.get_by_id(data_get['ticket_class_name'])
                data_save.class_name = class_name.key


                currency_ticket = CurrencyModel.get_by_id(data_get['ticket_currency'])
                data_save.currency = currency_ticket.key

                travel_ticket = TravelModel.get_by_id(data_get['ticket_travel'])
                data_save.travel = travel_ticket.key
                data = data_save.put()
            _ids.append(data.id())
    return _ids


def customer_api(url, tocken, segment, date=None):
    from ..customer.models_customer import CustomerModel
    from ..config.model_config import SynchroModel, AgencyModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))
    else:
        for data_get in result['customer']:
            old_data = CustomerModel.get_by_id(data_get['customer_id'])
            if old_data:
                old_data.first_name = data_get['customer_first_name']
                old_data.last_name = data_get['customer_last_name']
                old_data.birthday = function.date_convert(data_get['customer_birthday'])
                old_data.passport_number = data_get['customer_passport_number']
                old_data.nic_number = data_get['customer_nic_number']
                old_data.profession = data_get['customer_profession']
                old_data.nationality = data_get['customer_nationality']
                old_data.phone = data_get['customer_phone']
                old_data.dial_code = data_get['customer_dial_code']
                old_data.email = data_get['customer_email']
                old_data.is_new = data_get['customer_is_new']
                old_data.status = data_get['customer_status']
                old_data.put()
            else:
                data_save = CustomerModel(id=data_get['customer_id'])
                data_save.first_name = data_get['customer_first_name']
                data_save.last_name = data_get['customer_last_name']
                data_save.birthday = function.date_convert(data_get['customer_birthday'])
                data_save.passport_number = data_get['customer_passport_number']
                data_save.nic_number = data_get['customer_nic_number']
                data_save.profession = data_get['customer_profession']
                data_save.nationality = data_get['customer_nationality']
                data_save.phone = data_get['customer_phone']
                data_save.dial_code = data_get['customer_dial_code']
                data_save.email = data_get['customer_email']
                data_save.is_new = data_get['customer_is_new']
                data_save.status = data_get['customer_status']
                data_save.put()

        active_agency = AgencyModel.query(
            AgencyModel.local_status == True
        ).get()

        date_synchro = SynchroModel.query(
            SynchroModel.agency_synchro == active_agency.key
        ).order(-SynchroModel.date).get()

        date_synchro.time_customer = datetime.datetime.now().time()
        date_synchro.put()


def customer_api_put(url, tocken, segment, date):
    from ..customer.models_customer import CustomerModel
    from ..config.model_config import SynchroModel, AgencyModel
    import urllib

    date = function.datetime_convert(date)

    customer_new = CustomerModel.query(
        CustomerModel.date_update >= date
    )

    if customer_new:
        data = {}
        data['customer'] = []
        for customer in customer_new:
            data['customer'].append(customer.make_to_dict())

        data_format = urllib.urlencode(data)
        url = url+segment+tocken
        result = urlfetch.fetch(url=url, payload=data_format, method=urlfetch.POST, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        result = result.content
        result = json.loads(result)

        if result['status'] and result['status'] == 404:
            flash(result['message'], "warning")
        else:
            flash(result['message'], "success")

        active_agency = AgencyModel.query(
            AgencyModel.local_status == True
        ).get()

        date_synchro = SynchroModel.query(
            SynchroModel.agency_synchro == active_agency.key
        ).order(-SynchroModel.date).get()

        date_synchro.time_customer_put = datetime.datetime.now().time()
        date_synchro.put()


def ticket_allocated_api(url, tocken, segment, date):
    from ..ticket.models_ticket import TicketModel, CurrencyModel, TicketTypeNameModel, JourneyTypeModel, ClassTypeModel, TravelModel, AgencyModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))
    else:
        for data_get in result['ticket_allocated']:
            old_data = TicketModel.get_by_id(data_get['ticket_allocated_id'])
            if not old_data:
                data_save = TicketModel(id=data_get['ticket_allocated_id'])

                currency_ticket = CurrencyModel.get_by_id(data_get['sellpriceAgCurrency'])
                if currency_ticket:
                    data_save.sellpriceAg = data_get['sellpriceAg']
                    data_save.sellpriceAgCurrency = currency_ticket.key

                category_ticket = TicketTypeNameModel.get_by_id(data_get['type_name'])
                data_save.type_name = category_ticket.key

                journey_ticket = JourneyTypeModel.get_by_id(data_get['journey_name'])
                data_save.journey_name = journey_ticket.key

                classes_ticket = ClassTypeModel.get_by_id(data_get['class_name'])
                data_save.class_name = classes_ticket.key

                travel_ticket = TravelModel.get_by_id(data_get['travel_ticket'])
                data_save.travel_ticket = travel_ticket.key

                agency_ticket = AgencyModel.get_by_id(data_get['agency'])
                data_save.agency = agency_ticket.key

                data_save.is_prepayment = data_get['is_prepayment']
                data_save.statusValid = data_get['statusValid']
                data_save.is_return = data_get['is_return']
                data_save.selling = data_get['selling']
                data_save.is_ticket = data_get['is_ticket']
                data_save.datecreate = function.datetime_convert(data_get['datecreate'])

                data_save.put()


def get_doublons_ticket_return_api(url, tocken, segment, date):

    from ..ticket.models_ticket import TicketModel, CurrencyModel, CustomerModel,\
        TicketTypeNameModel, JourneyTypeModel, ClassTypeModel, TravelModel, AgencyModel, DepartureModel
    from ..config.model_config import SynchroModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))
    else:
        for data_get in result['tickets_return_sale']:
            old_data = TicketModel.get_by_id(data_get['ticket_allocated_id'])
            if not old_data:
                data_save = TicketModel(id=data_get['ticket_allocated_id'])

                currency_ticket = CurrencyModel.get_by_id(data_get['sellpriceAgCurrency'])
                if currency_ticket:
                    data_save.sellpriceAg = data_get['sellpriceAg']
                    data_save.sellpriceAgCurrency = currency_ticket.key

                currency_ticket = CurrencyModel.get_by_id(data_get['sellpriceCurrency'])
                if currency_ticket:
                    data_save.sellprice = data_get['sellprice']
                    data_save.sellpriceCurrency = currency_ticket.key

                category_ticket = TicketTypeNameModel.get_by_id(data_get['type_name'])
                data_save.type_name = category_ticket.key

                if data_get['journey_name']:
                    journey_ticket = JourneyTypeModel.get_by_id(data_get['journey_name'])
                    data_save.journey_name = journey_ticket.key

                classes_ticket = ClassTypeModel.get_by_id(data_get['class_name'])
                data_save.class_name = classes_ticket.key

                travel_ticket = TravelModel.get_by_id(data_get['travel_ticket'])
                data_save.travel_ticket = travel_ticket.key

                data_save.is_prepayment = data_get['is_prepayment']
                data_save.statusValid = data_get['statusValid']
                data_save.is_return = data_get['is_return']
                data_save.selling = data_get['selling']
                data_save.is_ticket = data_get['is_ticket']
                data_save.is_boarding = data_get['is_boarding']
                data_save.date_reservation = function.datetime_convert(data_get['date_reservation'])
                data_save.datecreate = function.datetime_convert(data_get['datecreate'])

                customer_ticket = CustomerModel.get_by_id(data_get['customer'])
                data_save.customer = customer_ticket.key

                departure_ticket = DepartureModel.get_by_id(data_get['departure'])
                data_save.departure = departure_ticket.key

                save = data_save.put()
                for child in data_get['child_return']:
                    duplicate_ticket = TicketModel(id=child['ticket_allocated_id'])
                    duplicate_ticket.type_name = category_ticket.key
                    duplicate_ticket.class_name = classes_ticket.key
                    duplicate_ticket.is_ticket = True
                    duplicate_ticket.is_count = False

                    duplicate_ticket.customer = customer_ticket.key

                    duplicate_ticket.parent_return = save

                    duplicate_ticket.put()
            else:

                category_ticket = TicketTypeNameModel.get_by_id(data_get['type_name'])
                classes_ticket = ClassTypeModel.get_by_id(data_get['class_name'])
                customer_ticket = CustomerModel.get_by_id(data_get['customer'])

                for child in data_get['child_return']:
                    duplicate_ticket = TicketModel(id=child['ticket_allocated_id'])
                    duplicate_ticket.type_name = category_ticket.key
                    duplicate_ticket.class_name = classes_ticket.key
                    duplicate_ticket.is_ticket = True
                    duplicate_ticket.is_count = False

                    duplicate_ticket.customer = customer_ticket.key

                    duplicate_ticket.parent_return = old_data.key

                    duplicate_ticket.put()

        active_agency = AgencyModel.query(
            AgencyModel.local_status == True
        ).get()

        date_synchro = SynchroModel.query(
            SynchroModel.agency_synchro == active_agency.key
        ).order(-SynchroModel.date).get()

        date_synchro.time_return_and_doublons_foreign = datetime.datetime.now().time()
        date_synchro.put()


def ticket_sale_put_api(url, tocken, segment, date):

    from ..ticket.models_ticket import TicketModel, AgencyModel
    from ..config.model_config import SynchroModel
    import urllib

    date = function.datetime_convert(date)

    data = {}
    data['ticket_sale'] = []

    ticket_sale = TicketModel.query(
        TicketModel.date_update >= date,
        TicketModel.selling == True,
        TicketModel.statusValid == True
    )

    active_local_agency = AgencyModel.query(
        AgencyModel.local_status == True
    ).get()

    for ticket in ticket_sale:
        if ticket.travel_ticket.get().destination_start == active_local_agency.destination:
            data['ticket_sale'].append(ticket.make_to_dict())

    data_format = urllib.urlencode(data)
    url = url+segment+tocken
    result = urlfetch.fetch(url=url, payload=data_format, method=urlfetch.POST, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    result = result.content
    result = json.loads(result)

    for ticket in ticket_sale:
        ticket.date_update = ticket.date_update
        ticket.put()

    if result['status'] and result['status'] == 404:
        flash(result['message'], "warning")
    else:
        flash(result['message'], "success")

    active_agency = AgencyModel.query(
        AgencyModel.local_status == True
    ).get()

    date_synchro = SynchroModel.query(
        SynchroModel.agency_synchro == active_agency.key
    ).order(-SynchroModel.date).get()

    date_synchro.time_ticket_sale_put = datetime.datetime.now().time()
    date_synchro.put()


def get_ticket_sale_online(url, tocken, segment, date):

    from ..ticket.models_ticket import TicketModel, CurrencyModel, CustomerModel, TicketTypeNameModel, JourneyTypeModel,\
        ClassTypeModel, TravelModel, AgencyModel, DepartureModel, UserModel
    from ..config.model_config import SynchroModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))
    else:
        for data_get in result['tickets_sale']:
            old_data = TicketModel.get_by_id(data_get['ticket_allocated_id'])
            if old_data:
                currency_ticket = CurrencyModel.get_by_id(data_get['sellpriceCurrency'])
                if currency_ticket:
                    old_data.sellprice = data_get['sellprice']
                    old_data.sellpriceCurrency = currency_ticket.key

                customer_ticket = CustomerModel.get_by_id(data_get['customer'])
                old_data.customer = customer_ticket.key

                departure_ticket = DepartureModel.get_by_id(data_get['departure'])
                old_data.departure = departure_ticket.key

                if data_get['parent_child']:
                    parent_child = TicketModel.get_by_id(data_get['parent_child'])
                    old_data.parent_child = parent_child.key

                user_ticket = UserModel.get_by_id(data_get['ticket_seller'])
                old_data.ticket_seller = user_ticket.key

                old_data.selling = data_get['selling']
                old_data.date_reservation = function.datetime_convert(data_get['date_reservation'])
                old_data.put()
            else:
                data_save = TicketModel(id=data_get['ticket_allocated_id'])

                currency_ticket = CurrencyModel.get_by_id(data_get['sellpriceAgCurrency'])
                if currency_ticket:
                    data_save.sellpriceAg = data_get['sellpriceAg']
                    data_save.sellpriceAgCurrency = currency_ticket.key

                category_ticket = TicketTypeNameModel.get_by_id(data_get['type_name'])
                data_save.type_name = category_ticket.key

                journey_ticket = JourneyTypeModel.get_by_id(data_get['journey_name'])
                data_save.journey_name = journey_ticket.key

                classes_ticket = ClassTypeModel.get_by_id(data_get['class_name'])
                data_save.class_name = classes_ticket.key

                travel_ticket = TravelModel.get_by_id(data_get['travel_ticket'])
                data_save.travel_ticket = travel_ticket.key

                agency_ticket = AgencyModel.get_by_id(data_get['agency'])
                data_save.agency = agency_ticket.key

                data_save.is_prepayment = data_get['is_prepayment']
                data_save.statusValid = data_get['statusValid']
                data_save.is_return = data_get['is_return']
                data_save.selling = data_get['selling']
                data_save.is_ticket = data_get['is_ticket']
                data_save.datecreate = function.datetime_convert(data_get['datecreate'])

                currency_ticket = CurrencyModel.get_by_id(data_get['sellpriceCurrency'])
                if currency_ticket:
                    data_save.sellprice = data_get['sellprice']
                    data_save.sellpriceCurrency = currency_ticket.key

                customer_ticket = CustomerModel.get_by_id(data_get['customer'])
                data_save.customer = customer_ticket.key

                departure_ticket = DepartureModel.get_by_id(data_get['departure'])
                data_save.departure = departure_ticket.key

                user_ticket = UserModel.get_by_id(data_get['ticket_seller'])

                if data_get['parent_child']:
                    parent_child = TicketModel.get_by_id(data_get['parent_child'])
                    data_save.parent_child = parent_child.key

                data_save.ticket_seller = user_ticket.key
                data_save.date_reservation = function.datetime_convert(data_get['date_reservation'])

                data_save.put()
        active_agency = AgencyModel.query(
            AgencyModel.local_status == True
        ).get()

        date_synchro = SynchroModel.query(
            SynchroModel.agency_synchro == active_agency.key
        ).order(-SynchroModel.date).get()

        date_synchro.time_ticket_sale_online = datetime.datetime.now().time()
        date_synchro.put()


def set_status_ticket_put():
    from ..ticket.models_ticket import TicketModel

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    ticket_status = TicketModel.query(
        TicketModel.statusValid == True,
        TicketModel.selling == True
    )

    for ticket in ticket_status:
        date_valid = ticket.date_reservation - function.datetime_convert(date_auto_nows)
        if date_valid.days >= 30 and not ticket.is_return:
            ticket.statusValid = False
            ticket.put()

        if date_valid.days >= 60 and ticket.is_return:
            ticket.statusValid = False
            ticket.put()


def get_ticket_return_foreign_disable(url, tocken, segment, date):

    from ..ticket.models_ticket import TicketModel

    url = ""+url+segment+tocken+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

    if result['status'] and result['status'] == 404:
        flash(result['message'], "danger")
        return redirect(url_for('Home'))
    else:
        for data_get in result['tickets_return_disabled']:
            old_data = TicketModel.get_by_id(data_get)
            if old_data:
                old_data.statusValid = False
                old_data.put()

