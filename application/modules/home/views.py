__author__ = 'wilrona'

from ...modules import *
from application import login_manager

from ..user.models_user import UserModel
from ..user.forms_user import FormLogin

cache = Cache(app)


@login_manager.user_loader
def load_user(userid):
    return UserModel.get_by_id(userid)


@app.route('/set_session')
def set_session():
    session.permanent = True
    return json.dumps({
        'statut': True
    })


@app.route('/', methods=['POST', 'GET'])
def Home():

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    if 'user_id' in session:
        return redirect(url_for('Dashboard'))

    from ..user.models_user import RoleModel, UserRoleModel, UserModel, AgencyModel, ProfilModel, ProfilRoleModel, CurrencyModel
    from ..destination.models_destination import DestinationModel
    from ..config.model_config import ConfigModel, SynchroModel

    admin_role = RoleModel.query(
        RoleModel.name == "super_admin"
    ).get()

    # Verification de l'exitance d'un profil super admin dans la base de donnee
    exist_super_admin = 0
    if admin_role:
        exist_super_admin = UserRoleModel.query(
            UserRoleModel.role_id == admin_role.key
        ).count()

    # Verification de l'existance d'une agence active dans la BD
    exist_config_active = AgencyModel.query(
        AgencyModel.local_status == True
    ).count()
    current_agency = None

    exist = False
    verified_token = 1
    config_agency = None

    form = FormLogin(request.form)

    if exist_super_admin >= 1 and exist_config_active >= 1:
        exist = True
        verified_token = 0
        #information de l'agence active
        exist_agency = AgencyModel.query(
            AgencyModel.local_status == True
        ).get()
        #information de configuration de l'agence
        config_agency = ConfigModel.query(
            ConfigModel.local_ref == exist_agency.key
        ).get()



        form.token.data = config_agency.token_agency
        form.url.data = config_agency.url_server

    # Controle d'une redirection possible vers la precedente page avant deconnexion
    url = None
    if request.args.get('url'):
        url = request.args.get('url')

    if form.validate_on_submit():
        try:
            password = hashlib.sha224(form.password.data).hexdigest()
        except UnicodeEncodeError:
            flash('Username or Password is invalid', 'danger')
            return redirect(url_for('Home'))

        user_login = UserModel.query(
            UserModel.email == form.email.data,
            UserModel.password == password
        ).get()

        if not user_login:

            if exist_config_active >= 1:
                url = ""+config_agency.url_server+"/login_user/get/"+password+"/"+form.email.data+"/"+config_agency.token_agency+"?exist="+str(verified_token)
            else:
                url = "http://"+form.url.data+"/login_user/get/"+password+"/"+form.email.data+"/"+form.token.data+"?exist="+str(verified_token)

            result = urlfetch.fetch(url)
            result = result.content
            result = json.loads(result)

            if result['status'] and result['status'] == 404:
                flash('Username or Password is invalid', 'danger')
            elif result['status'] and result['status'] == 403:
                flash(result['message'], 'danger')
            elif result['status'] and result['status'] == 400:
                flash(result['message'], 'danger')
                form.token.errors.append(result['message'])
            else:

                user_log = UserModel(id=result['user']['user_id'])
                user_log.first_name = result['user']['first_name']
                user_log.last_name = result['user']['last_name']
                user_log.dial_code = result['user']['dial_code']
                user_log.enabled = result['user']['enabled']
                user_log.email = result['user']['email']
                user_log.password = result['user']['password']
                user_log.phone = result['user']['phone']

                if not result['profil_user']:
                    user_save = user_log.put()
                    # Traitement des informations du super administrateur
                    if result['role_user']:
                        role_exist = RoleModel.get_by_id(result['role_user']['role_user_id'])

                        if not role_exist:
                            role_user = RoleModel(id=result['role_user']['role_user_id'])
                            role_user.name = result['role_user']['role_user_name']
                            role_user.visible = result['role_user']['role_user_visible']
                            role_save = role_user.put()
                        else:
                            role_save = role_exist.key

                        user_role = UserRoleModel()
                        user_role.role_id = role_save
                        user_role.user_id = user_save
                        user_role.put()

                else:

                    # traitement des informations des utilisateurs non administrateur
                    profil_exist = ProfilModel.get_by_id(result['profil_user']['profil_id'])
                    if profil_exist:
                        profil_user = ProfilModel(id=result['profil_user']['profil_id'])
                        profil_user.name = result['profil_user']['profil_name']
                        profil_user.standard = result['profil_user']['profil_standard']
                        profil_user.enable = result['profil_user']['profil_enable']
                        profil_save = profil_user.put()
                    else:
                        profil_save = profil_exist.key

                    user_log.profil = profil_save
                    user_save = user_log.put()

                    for role in result['profil_user']['profil_roles']:

                        role_exist = RoleModel.get_by_id(role['role_id'])

                        if not role_exist:
                            role_user = RoleModel(id=role['role_id'])
                            role_user.name = role['role_name']
                            role_user.visible = role['role_visible']
                            role_save = role_user.put()
                        else:
                            role_save = role_exist.key

                        user_role = UserRoleModel()
                        user_role.role_id = role_save
                        user_role.user_id = user_save
                        user_role.put()

                        user_profil = ProfilRoleModel()
                        user_profil.role_id = role_save
                        user_profil.profil_id = profil_save


                if not exist_config_active >= 1:

                    currency = CurrencyModel(id=result['current_agency']['agency_destination']['destination_currency']['currency_id'])
                    currency.code = result['current_agency']['agency_destination']['destination_currency']['currency_code']
                    currency.name = result['current_agency']['agency_destination']['destination_currency']['currency_name']
                    currency_save = currency.put()

                    destination = DestinationModel(id=result['current_agency']['agency_destination']['destination_id'])
                    destination.code = result['current_agency']['agency_destination']['destination_code']
                    destination.name = result['current_agency']['agency_destination']['destination_name']
                    destination.currency = currency_save
                    destination_save = destination.put()

                    agency = AgencyModel(id=result['current_agency']['agency_id'])
                    agency.name = result['current_agency']['agency_name']
                    agency.country = result['current_agency']['agency_country']
                    agency.phone = result['current_agency']['agency_phone']
                    agency.fax = result['current_agency']['agency_fax']
                    agency.address = result['current_agency']['agency_address']
                    agency.reduction = result['current_agency']['agency_reduction']
                    agency.is_achouka = result['current_agency']['agency_is_achouka']
                    agency.status = result['current_agency']['agency_status']
                    agency.local_status = True
                    agency.destination = destination_save
                    agency_save = agency.put()


                    config = ConfigModel()
                    config.url_server = "http://"+form.url.data
                    config.token_agency = form.token.data
                    config.local_ref = agency_save
                    config.put()

                    flash('Agency Synchronize', 'success')
                    return redirect(url_for('Home'))
        else:
            if not user_login.is_active():
                flash('Your account is disabled. Contact Administrator', 'danger')
                return redirect(url_for('Home', url=url))

            agency = 0
            if user_login.agency:
                agency = user_login.agency.get().key.id()
                if not agency.status:
                    flash('Your agency is disabled in online apps. Contact Administrator', 'danger')
                    return redirect(url_for('Home', url=url))

                if not agency.local_status:
                    flash('You can not connect in local. Your agency is disabled. Contact Administrator', 'danger')
                    return redirect(url_for('Home', url=url))

            #implementation de l'heure local
            time_zones = pytz.timezone('Africa/Douala')
            date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

            session['user_id'] = user_login.key.id()
            session['agence_id'] = agency
            user_login.logged = True
            user_login.date_last_logged = function.datetime_convert(date_auto_nows)
            this_login = user_login.put()

            if url:
                return redirect(url)

            return redirect(url_for('Dashboard'))

    synchro = None
    if config_agency:
        synchro = SynchroModel.query(
            SynchroModel.agency_synchro == config_agency.local_ref
        ).order(-SynchroModel.date).get()

    # Affichage de la connexion au serveur
    connexion = True
    if exist:
        try:
            url = ""+config_agency.url_server
            result = urlfetch.fetch(url)
            if result.status_code != 200:
                connexion = False
        except urlfetch.DownloadError:
            connexion = False

    # autorisation de la synchronisation
    synchronize = False
    if synchro:
        date_today = datetime.date.today()
        delta = datetime.timedelta(hours=24)
        date_syncho = synchro.date + delta
        if date_syncho <= date_today and exist:
            synchronize = True
    elif exist:
        synchronize = True

    return render_template('index/home.html', **locals())


@app.route('/logout_user')
def logout_user():
    if 'user_id' in session:
        user_id = session.get('user_id')
        UserLogout = UserModel.get_by_id(int(user_id))
        UserLogout.logged = False
        change = UserLogout.put()
        if change:
            session.pop('user_id')
            session.pop('agence_id')
    return redirect(url_for('Home'))


@app.route('/dashboard')
@login_required
def Dashboard():
    menu = 'dashboard'
    from ..ticket.models_ticket import AgencyModel, TicketModel

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    #TRAITEMENT DU TRAFIC GABON
    all_agency = AgencyModel.query()

    the_ticket_agency_gabon = []
    the_ticket_agency_cm_ngn = []

    time_minus_14days = datetime.datetime.now(time_zones) - datetime.timedelta(days=14)
    time_minus_14days = time_minus_14days.strftime("%Y-%m-%d %H:%M:%S")

    month_current = function.datetime_convert(date_auto_nows).month

    # TRAITEMENT DU DASHBOARD DE SELLER
    if not current_user.has_roles(('admin', 'manager_agency', 'super_admin')) and current_user.has_roles('employee_POS'):

        user_ticket = TicketModel.query(
            TicketModel.ticket_seller == current_user.key,
            TicketModel.selling == True,
            TicketModel.is_count == True
        ).order(-TicketModel.date_reservation)

        agency_user = AgencyModel.get_by_id(int(session.get('agence_id')))

        user_ticket_tab = []
        for ticket in user_ticket:
            tickets = {}
            tickets['class'] = ticket.class_name
            tickets['journey'] = ticket.journey_name
            tickets['type'] = ticket.type_name
            tickets['travel'] = ticket.travel_ticket
            tickets['price'] = ticket.sellprice
            tickets['currency'] = ticket.sellpriceCurrency.get().code
            user_ticket_tab.append(tickets)

        groupers = itemgetter("class", "type", "journey", "travel")

        the_ticket_sale = []
        for key, grp in groupby(sorted(user_ticket_tab, key=groupers), groupers):
            temp_dict = dict(zip(["class", "type", "journey", "travel"], key))
            temp_dict['number'] = 0
            temp_dict['price'] = 0
            for item in grp:
                temp_dict['number'] += 1
                temp_dict['price'] += item['price']
                temp_dict['currency'] = item['currency']
            the_ticket_sale.append(temp_dict)

        from ..transaction.models_transaction import ExpensePaymentTransactionModel

        local_tocal = 0
        user_tickets_tab = []
        for ticket in user_ticket:

            expensepayment_query = ExpensePaymentTransactionModel.query(
                ExpensePaymentTransactionModel.ticket == ticket.key
            )

            #RECUPERATION DES TICKETS QUE L'ON VA SOLDER
            number_attend_payment = 0
            transaction_amount = 0
            for transaction_line in expensepayment_query:
                if transaction_line.transaction.get().is_payment is True and transaction_line.is_difference is False:
                    number_attend_payment += 1
                    transaction_amount += transaction_line.amount


            # Calcul du montant total
            if ticket.travel_ticket.get().destination_start == agency_user.destination:

                if number_attend_payment == 0 and not transaction_amount:
                    local_tocal += ticket.sellprice

                if number_attend_payment >= 1 and ticket.sellprice > transaction_amount:
                    local_tocal += ticket.sellprice - transaction_amount

            # recuperation des tickets non locaux
            if ticket.travel_ticket.get().destination_start != agency_user.destination:

                tickets = {}
                if number_attend_payment == 0 and not transaction_amount:
                    tickets['travel'] = ticket.travel_ticket
                    tickets['amount'] = ticket.sellprice
                    tickets['currency'] = ticket.sellpriceCurrency.get().code
                    user_tickets_tab.append(tickets)

                if number_attend_payment >= 1 and ticket.sellprice > transaction_amount:
                    tickets['travel'] = ticket.travel_ticket
                    tickets['amount'] = ticket.sellprice - transaction_amount
                    tickets['currency'] = ticket.sellpriceCurrency.get().code
                    user_tickets_tab.append(tickets)

        groupers_2 = itemgetter("travel", "currency")

        the_amount_foreign_sale = []
        for key, grp in groupby(sorted(user_tickets_tab, key=groupers_2), groupers_2):
            temp_dict = dict(zip(["travel", "currency"], key))
            temp_dict['price'] = 0
            for item in grp:
                temp_dict['price'] += item['amount']
            the_amount_foreign_sale.append(temp_dict)

        return render_template('/index/dashboard_pos.html', **locals())


    # TRAITEMENT DU DASHBOARD DU MANAGER
    if not current_user.has_roles(('admin','super_admin')) and current_user.has_roles('manager_agency'):

        user_agency = AgencyModel.get_by_id(int(session.get('agence_id')))

        ticket_agency = TicketModel.query(
            TicketModel.agency == user_agency.key,
            TicketModel.selling == True,
            TicketModel.is_count == True,
            TicketModel.date_reservation <= function.datetime_convert(date_auto_nows),
            TicketModel.date_reservation > function.datetime_convert(time_minus_14days)
        )
        the_ticket_agency_tab = []
        for ticket in ticket_agency:
            tickets = {}
            tickets['date'] = function.format_date(ticket.departure.get().departure_date, "%Y-%m-%d")
            tickets['departure'] = ticket.departure
            tickets['departure_start'] = ticket.departure.get().destination.get().destination_start.get().name
            tickets['departure_check'] = ticket.departure.get().destination.get().destination_check.get().name
            tickets['heure'] = function.format_date(function.add_time(ticket.departure.get().schedule, ticket.departure.get().time_delay), "%H:%M:%S")
            tickets['price'] = ticket.sellprice
            tickets['currency'] = ticket.sellpriceCurrency.get().code
            the_ticket_agency_tab.append(tickets)
        else:
            tickets = {}
            tickets['date'] = function.format_date(datetime.datetime.now(), "%Y-%m-%d")
            tickets['departure'] = '11111111111'
            tickets['departure_start'] = "No destination start"
            tickets['departure_check'] = "No destination check"
            tickets['heure'] = function.format_date(datetime.datetime.now().time(), "%H:%M:%S")
            tickets['price'] = 0
            tickets['currency'] = user_agency.destination.get().currency.get().code
            the_ticket_agency_tab.append(tickets)

        grouper = itemgetter("date", "heure", "departure", "currency")

        the_ticket_agency = []
        for key, grp in groupby(sorted(the_ticket_agency_tab, key=grouper), grouper):
            temp_dict = dict(zip(["date", "heure", "departure", "currency"], key))
            temp_dict['price'] = 0
            for item in grp:
                temp_dict['departure_start'] = item['departure_start']
                temp_dict['departure_check'] = item['departure_check']
                temp_dict['price'] += item['price']
            the_ticket_agency.append(temp_dict)

        heure = function.datetime_convert(date_auto_nows).time()

        from ..departure.models_departure import DepartureModel

        departure = DepartureModel.query(
            DepartureModel.departure_date == datetime.date.today(),
            DepartureModel.schedule >= heure
        ).order(
            -DepartureModel.departure_date,
            DepartureModel.schedule,
            DepartureModel.time_delay
        )

        for dep in departure:
            if dep.destination.get().destination_start == user_agency.destination:
                current_departure = dep
                break

        for dep in departure:
            if dep.destination.get().destination_check == user_agency.destination:
                current_departure_check = dep
                break

        departure_current = DepartureModel.query(
            DepartureModel.departure_date == datetime.date.today(),
            DepartureModel.schedule < heure
        ).order(
            -DepartureModel.departure_date,
            DepartureModel.schedule,
            DepartureModel.time_delay
        )

        for dep in departure_current:
            interval = datetime.datetime.combine(datetime.date.today(), heure) - datetime.datetime.combine(dep.departure_date, function.add_time(dep.schedule, dep.time_delay))
            time_travel = function.time_convert(dep.destination.get().time)
            time_travel = datetime.timedelta(hours=time_travel.hour, minutes=time_travel.minute)
            if interval <= time_travel:
                current_departure_in_progress = dep
                break


        ticket_agency = TicketModel.query(
            TicketModel.agency == user_agency.key,
            TicketModel.selling == True,
            TicketModel.is_count == True
        )

        ticket_sale_local = {}
        ticket_sale_local['price'] = 0
        ticket_sale_local['number'] = 0
        for ticket in ticket_agency:
            if function.datetime_convert(ticket.date_reservation).month == month_current and ticket.travel_ticket.get().destination_start == user_agency.destination:
                ticket_sale_local['price'] += ticket.sellprice
                ticket_sale_local['number'] += 1
                ticket_sale_local['currency'] = ticket.sellpriceCurrency.get().code

        ticket_sale_foreign_tab = []
        for ticket in ticket_agency:
            if function.datetime_convert(ticket.date_reservation).month == month_current and ticket.travel_ticket.get().destination_start != user_agency.destination:
                ticket_sale_foreign = {}
                ticket_sale_foreign['travel'] = ticket.travel_ticket
                ticket_sale_foreign['price'] = ticket.sellprice
                ticket_sale_foreign['number'] = 1
                ticket_sale_foreign['currency'] = ticket.sellpriceCurrency.get().code
                ticket_sale_foreign_tab.append(ticket_sale_foreign)

        groupers = itemgetter("travel", "currency")

        the_ticket_sale_foreign = []
        for key, grp in groupby(sorted(ticket_sale_foreign_tab, key=groupers), groupers):
            temp_dict = dict(zip(["travel", "currency"], key))
            temp_dict['price'] = 0
            temp_dict['number'] = 0
            for item in grp:
                temp_dict['price'] += item['price']
                temp_dict['number'] += item['number']
            the_ticket_sale_foreign.append(temp_dict)

        return render_template('/index/dashboard_manager.html', **locals())

    # Redirection d'un utilisateur employe boarding
    if not current_user.has_roles(('admin', 'manager_agency', 'super_admin', 'employee_POS')) and current_user.has_roles('employee_Boarding'):
        return redirect(url_for('Boarding'))

    from ..config.model_config import ConfigModel, SynchroModel

    list_conf = ConfigModel.query()
    list_sync = SynchroModel.query().order(-SynchroModel.date).get()

    return render_template('/index/dashboard.html', **locals())

@app.route('/settings')
@login_required
@roles_required(('admin', 'super_admin'))
def Settings():

    menu = 'settings'
    return render_template('/index/settings.html', **locals())


@app.route('/recording')
@login_required
@roles_required(('manager_agency', 'super_admin'))
def Recording():

    menu = 'recording'
    return render_template('/index/recording.html', **locals())