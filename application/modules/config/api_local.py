__author__ = 'Vercossa'

from ...modules import *


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route('/get_departure_api/<int:url>/<int:segment>')
def get_departure_api(url, segment):

    from ..config.model_config import ConfigModel, AgencyModel, SynchroModel

    active_agency = AgencyModel.query(
        AgencyModel.local_status == True
    ).get()

    token_active = ConfigModel.query(
        ConfigModel.local_ref == active_agency.key
    ).get()

    date_synchro = SynchroModel.query(
        SynchroModel.agency_synchro == active_agency.key
    ).order(-SynchroModel.date).get()

    from ..departure.models_departure import DepartureModel, TravelModel, VesselModel

    if not date_synchro.time_departure:
        date = date_synchro.time_all
    else:
        date = date_synchro.time_departure

    url = ""+url+segment+token_active.token_agency+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

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

    date_synchro.time_departure = datetime.datetime.now().time()
    date_synchro.put()
    return "true"

@app.route('/get_customer_api/<int:url>/<int:segment>')
def get_customer_api(url, segment):

    from ..config.model_config import ConfigModel, AgencyModel, SynchroModel

    active_agency = AgencyModel.query(
        AgencyModel.local_status == True
    ).get()

    token_active = ConfigModel.query(
        ConfigModel.local_ref == active_agency.key
    ).get()

    date_synchro = SynchroModel.query(
        SynchroModel.agency_synchro == active_agency.key
    ).order(-SynchroModel.date).get()

    if not date_synchro.time_customer:
        date = date_synchro.time_all
    else:
        date = date_synchro.time_customer

    from ..customer.models_customer import CustomerModel

    url = ""+url+segment+token_active.token_agency+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

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

    date_synchro.time_customer = datetime.datetime.now().time()
    date_synchro.put()
    return "True"


@app.route('/send_customer_api/<int:url>/<int:segment>')
def send_customer_api(url, segment):

    from ..config.model_config import ConfigModel, AgencyModel, SynchroModel

    active_agency = AgencyModel.query(
        AgencyModel.local_status == True
    ).get()

    token_active = ConfigModel.query(
        ConfigModel.local_ref == active_agency.key
    ).get()

    date_synchro = SynchroModel.query(
        SynchroModel.agency_synchro == active_agency.key
    ).order(-SynchroModel.date).get()

    from ..customer.models_customer import CustomerModel
    import urllib

    if not date_synchro.time_customer_put:
        date = date_synchro.time_all
    else:
        date = date_synchro.time_customer_put

    customer_new = CustomerModel.query(
        CustomerModel.date_update >= date
    )

    data = {'customer': []}

    for customer_new in customer_new:
        data['customer'].append(customer_new.make_to_dict())


    data_format = urllib.urlencode(data)
    url = url+segment+token_active.token_agency
    urlfetch.fetch(url=url, payload=data_format, method=urlfetch.POST, headers={'Content-Type': 'application/x-www-form-urlencoded'})

    date_synchro.time_customer_put = datetime.datetime.now().time()
    date_synchro.put()

    return "True"


@app.route('/send_ticket_sale_api/<int:url>/<int:segment>')
def send_ticket_sale_api(url, segment):

    from ..config.model_config import ConfigModel, AgencyModel, SynchroModel

    active_agency = AgencyModel.query(
        AgencyModel.local_status == True
    ).get()

    token_active = ConfigModel.query(
        ConfigModel.local_ref == active_agency.key
    ).get()

    date_synchro = SynchroModel.query(
        SynchroModel.agency_synchro == active_agency.key
    ).order(-SynchroModel.date).get()

    from ..ticket.models_ticket import TicketModel, ndb
    import urllib

    if not date_synchro.time_ticket_sale_put:
        date = date_synchro.time_all
    else:
        date = date_synchro.time_ticket_sale_put

    ticket_sale = TicketModel.query(
        TicketModel.date_update >= date,
        TicketModel.selling == True,
        TicketModel.statusValid == True
    )

    data = {}
    data['ticket_sale'] = []

    for ticket in ticket_sale:
        if ticket.travel_ticket.get().destination_start == active_agency.destination:
            data['ticket_sale'].append(ticket.make_to_dict())


    data_format = urllib.urlencode(data)
    url = url+segment+token_active.token_agency
    urlfetch.fetch(url=url, payload=data_format, method=urlfetch.POST, headers={'Content-Type': 'application/x-www-form-urlencoded'})

    ticket_sale = TicketModel.query(
        TicketModel.date_update >= date,
        TicketModel.selling == True,
        TicketModel.statusValid == False,
        ndb.OR(
            TicketModel.generate_boarding == True,
            TicketModel.is_boarding == True
        )

    )

    data = {}
    data['ticket_sale'] = []

    for ticket in ticket_sale:
        if ticket.travel_ticket.get().destination_start == active_agency.destination:
            data['ticket_sale'].append(ticket.make_to_dict())


    data_format = urllib.urlencode(data)
    url = url+segment+token_active.token_agency
    urlfetch.fetch(url=url, payload=data_format, method=urlfetch.POST, headers={'Content-Type': 'application/x-www-form-urlencoded'})


    date_synchro.time_ticket_sale_put = datetime.datetime.now().time()
    date_synchro.put()

    return "True"


@app.route('/set_change_status_ticket_api')
def set_change_status_ticket_api():

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

    return "True"


@app.route('/get_ticket_sale_online_api/<int:url>/<int:segment>')
def get_ticket_sale_online_api(url, segment):

    from ..config.model_config import ConfigModel, AgencyModel, SynchroModel

    active_agency = AgencyModel.query(
        AgencyModel.local_status == True
    ).get()

    token_active = ConfigModel.query(
        ConfigModel.local_ref == active_agency.key
    ).get()

    date_synchro = SynchroModel.query(
        SynchroModel.agency_synchro == active_agency.key
    ).order(-SynchroModel.date).get()

    if not date_synchro.time_ticket_sale_online:
        date = date_synchro.time_all
    else:
        date = date_synchro.time_ticket_sale_online

    from ..ticket.models_ticket import TicketModel, CurrencyModel, CustomerModel, TicketTypeNameModel, JourneyTypeModel,\
        ClassTypeModel, TravelModel, AgencyModel, DepartureModel, UserModel

    url = ""+url+segment+token_active.token_agency+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

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

    date_synchro.time_ticket_sale_online = datetime.datetime.now().time()
    date_synchro.put()
    return "True"


@app.route('/get_doublons_ticket_return_api/<int:url>/<int:segment>')
def get_doublons_ticket_return_api(url, segment):

    from ..config.model_config import ConfigModel, AgencyModel, SynchroModel

    active_agency = AgencyModel.query(
        AgencyModel.local_status == True
    ).get()

    token_active = ConfigModel.query(
        ConfigModel.local_ref == active_agency.key
    ).get()

    date_synchro = SynchroModel.query(
        SynchroModel.agency_synchro == active_agency.key
    ).order(-SynchroModel.date).get()

    if not date_synchro.time_return_and_doublons_foreign:
        date = date_synchro.time_all
    else:
        date = date_synchro.time_return_and_doublons_foreign

    from ..ticket.models_ticket import TicketModel, CurrencyModel, CustomerModel,\
        TicketTypeNameModel, JourneyTypeModel, ClassTypeModel, TravelModel, DepartureModel

    url = ""+url+segment+token_active.token_agency+"?last_update="+str(date)
    result = urlfetch.fetch(url)
    result = result.content
    result = json.loads(result)

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
    date_synchro.time_return_and_doublons_foreign = datetime.datetime.now().time()
    date_synchro.put()
    return "True"


@app.route('/date_last_synchro')
def date_last_synchro():

    from ..config.model_config import ConfigModel, AgencyModel, SynchroModel

    active_agency = AgencyModel.query(
        AgencyModel.local_status == True
    ).get()

    date_synchro = SynchroModel.query(
        SynchroModel.agency_synchro == active_agency.key
    ).order(-SynchroModel.date).get()

    data = {}
    data['last_date'] = str(date_synchro.date)

    resp = jsonify(data)
    return resp


@app.route('/next_journey_agency')
def next_journey_agency():

    from ..departure.models_departure import DepartureModel
    from ..agency.models_agency import AgencyModel

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    today = function.datetime_convert(date_auto_nows)


    departure = DepartureModel.query(
        DepartureModel.departure_date >= datetime.date.today()
    ).order(
        DepartureModel.departure_date,
        DepartureModel.schedule,
        DepartureModel.time_delay
    )

    active_agency = AgencyModel.query(
        AgencyModel.local_status == True
    ).get()

    data = {}
    for dep in departure:
        departure_time = function.add_time(dep.schedule, dep.time_delay)
        departure_datetime = datetime.datetime(dep.departure_date.year, dep.departure_date.month, dep.departure_date.day, departure_time.hour, departure_time.minute, departure_time.second)
        if dep.destination.get().destination_start == active_agency.destination and departure_datetime > today:
            current_departure = dep
            data['date'] = str(current_departure.departure_date)
            data['time'] = str(function.add_time(current_departure.schedule, current_departure.time_delay))
            break

    resp = jsonify(data)
    return resp




