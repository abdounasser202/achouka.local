__author__ = 'wilrona'

from ...modules import *

from models_ticket_type import TicketTypeModel, TicketTypeNameModel, ClassTypeModel, JourneyTypeModel, TravelModel, CurrencyModel
from ..agency.models_agency import AgencyModel
from forms_ticket_type import FormTicketType, FormJourneyType, FormClassType, FormTicketTypeName


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route('/settings/ticket')
@login_required
@roles_required(('admin', 'super_admin'))
def TicketType_Index():
    menu = 'settings'
    submenu = 'tickettype'

    tickettype = TicketTypeModel.query()

    from ..activity.models_activity import ActivityModel
    feed = ActivityModel.query(
        ActivityModel.object == 'TicketTypeModel',
    ).order(
        -ActivityModel.time
    )

    feed_tab = []
    count = 0
    for feed in feed:
        feed_list = {}
        feed_list['user'] = feed.user_modify
        vess = TicketTypeModel.get_by_id(feed.identity)
        if vess:
            feed_list['data'] = vess.name+" ("+vess.class_name.get().name+" - "+vess.type_name.get().name+" - "+vess.journey_name.get().name+")"
        else:
            feed_list['data'] = feed.last_value
        feed_list['time'] = feed.time
        feed_list['nature'] = feed.nature
        feed_list['id'] = feed.identity
        feed_tab.append(feed_list)
        count += 1
        if count > 5 and not request.args.get('modal'):
            count += 1
            break

    if request.args.get('modal'):
        return render_template('/tickettype/all_feed.html', **locals())

    return render_template('/tickettype/index.html', **locals())


@app.route('/settings/ticket/edit/<int:tickettype_id>', methods=['POST', 'GET'])
@app.route('/settings/ticket/edit', methods=['POST', 'GET'])
@login_required
@roles_required(('admin', 'super_admin'))
def TicketType_Edit(tickettype_id=None):
    menu = 'settings'
    submenu = 'tickettype'

    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    #liste des voyages
    listTravel = TravelModel.query().order(TravelModel.destination_start)

    #liste des ticket type name
    listTicketType = TicketTypeNameModel.query().order(TicketTypeModel.name)

    #liste des classes de ticket
    listClassTicket = ClassTypeModel.query().order(ClassTypeModel.name)

    #liste des journey
    listJourneyTicket = JourneyTypeModel.query().order(JourneyTypeModel.name)
    #Compter le nombre de journey avec la function retour active
    returnjourney = JourneyTypeModel.query(
        JourneyTypeModel.returned == True
    ).count()

    feed_tab = []

    if tickettype_id:

        tickettype = TicketTypeModel.get_by_id(tickettype_id)
        form = FormTicketType(obj=tickettype)

        form_currency = CurrencyModel.get_by_id(int(tickettype.currency.get().key.id()))
        form_currency = form_currency.code

        form_travel = tickettype.travel.get().key.id()

        feed = ActivityModel.query(
            ActivityModel.object == 'TicketTypeModel',
            ActivityModel.identity == tickettype.key.id()
        ).order(
            -ActivityModel.time
        )

        count = 0
        for feed in feed:
            feed_list = {}
            feed_list['user'] = feed.user_modify
            vess = TicketTypeModel.get_by_id(feed.identity)
            feed_list['data'] = feed.last_value
            if vess:
                feed_list['data'] = vess.name+" ("+vess.class_name.get().name+" - "+vess.type_name.get().name+" - "+vess.journey_name.get().name+")"
            feed_list['time'] = feed.time
            feed_list['nature'] = feed.nature
            feed_list['id'] = feed.identity
            feed_tab.append(feed_list)
            count += 1
            if count > 5:
                count += 1
                break

    else:
        tickettype = TicketTypeModel()
        form = FormTicketType(request.form)

        if form.currency.data:
            form_currency = CurrencyModel.get_by_id(int(form.currency.data))
            form_currency = form_currency.code

    if form.validate_on_submit():
        #recuperation des informations de selection
        currency = CurrencyModel.get_by_id(int(form.currency.data))
        type_name = TicketTypeNameModel.get_by_id(int(form.type_name.data))
        class_name = ClassTypeModel.get_by_id(int(form.class_name.data))
        journey_name = JourneyTypeModel.get_by_id(int(form.journey_name.data))
        travel = TravelModel.get_by_id(int(form.travel.data))

        tickettype.name = form.name.data
        tickettype.type_name = type_name.key
        tickettype.journey_name = journey_name.key
        tickettype.class_name = class_name.key
        tickettype.currency = currency.key
        tickettype.price = form.price.data
        tickettype.travel = travel.key

        this_ticket = tickettype.put()

        activity = ActivityModel()
        activity.user_modify = current_user.key
        activity.identity = this_ticket.id()
        activity.object = "TicketTypeModel"
        activity.time = function.datetime_convert(date_auto_nows)

        if tickettype_id:
            activity.nature = 4
            flash(u' Ticket Type Updated!', 'success')
        else:
            activity.nature = 1
            flash(u' Ticket Type Saved!', 'success')
        activity.put()

        return redirect(url_for('TicketType_Index'))

    return render_template('/tickettype/edit.html', **locals())


@app.route('/Active_tickettype/<int:tickettype_id>')
@login_required
@roles_required(('admin', 'super_admin'))
def Active_tickettype(tickettype_id):

    tickettype_active = TicketTypeModel.get_by_id(tickettype_id)

    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    activity = ActivityModel()
    activity.user_modify = current_user.key
    activity.identity = tickettype_active.key.id()
    activity.object = "TicketTypeModel"
    activity.time = function.datetime_convert(date_auto_nows)

    if not tickettype_active.active:
        tickettype_exit = TicketTypeModel.query(
            TicketTypeModel.type_name == tickettype_active.type_name,
            TicketTypeModel.class_name == tickettype_active.class_name,
            TicketTypeModel.journey_name == tickettype_active.journey_name,
            TicketTypeModel.travel == tickettype_active.travel,
            TicketTypeModel.active == True
        ).count()

        if tickettype_exit >= 1:
            flash(' Other ticket type have Class = '+str(tickettype_active.class_name.get().name)
                  +', Type  = '+str(tickettype_active.type_name.get().name)+' and Journey = '
                  +str(tickettype_active.journey_name.get().name)+'from '+str(tickettype_active.travel.get().destination_start.get().name)+" to "+str(tickettype_active.travel.get().destination_check.get().name)+" is activated", 'danger')
        else:
            activity.nature = 5
            tickettype_active.active = True
    else:
        activity.nature = 2
        tickettype_active.active = False

    activity.put()
    tickettype_active.put()
    return redirect(url_for('TicketType_Index'))

@app.route('/delete_tickettype/<int:tickettype_id>')
@login_required
@roles_required(('admin', 'super_admin'))
def delete_tickettype(tickettype_id):

    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    #recuperer la cle de la devise equivalence
    TicketType_delete = TicketTypeModel.get_by_id(tickettype_id)

    del_activity = ActivityModel.query(
            ActivityModel.object == "TicketTypeModel",
            ActivityModel.identity == TicketType_delete.key.id()
    )

    for del_act in del_activity:
        del_act.key.delete()

    activity = ActivityModel()
    activity.user_modify = current_user.key
    activity.identity = TicketType_delete.key.id()
    activity.object = "TicketTypeModel"
    activity.time = function.datetime_convert(date_auto_nows)
    activity.nature = 3
    activity.last_value = TicketType_delete.name+" ("+TicketType_delete.class_name.get().name+" - "+TicketType_delete.type_name.get().name+" - "+TicketType_delete.journey_name.get().name+")"
    activity.put()

    flash(u' Ticket Deleted: ' + TicketType_delete.name, 'success')
    TicketType_delete.key.delete()
    return redirect(url_for('TicketType_Index'))



@app.route('/Currency_Travel')
@app.route('/Currency_Travel/<int:travel_id>')
@login_required
@roles_required(('admin', 'super_admin'))
def Currency_Travel(travel_id=None):

    travel = None
    if travel_id:
        travel = TravelModel.get_by_id(travel_id)

    if travel:
        data = json.dumps({
            'statut': 'OK',
            'currency': travel.destination_start.get().currency.get().code,
            'id': travel.destination_start.get().currency.get().key.id(),
        }, sort_keys=True)
    else:
        data = json.dumps({
            'statut': 'error',
            'value': 'Choice travel'
        }, sort_keys=True)

    return data

@app.route('/Verified_Disabled/<int:tickettype_id>')
@login_required
@roles_required(('admin', 'super_admin'))
def Verified_Disabled(tickettype_id):
    from ..ticket.models_ticket import TicketModel
    TicketType_delete = TicketTypeModel.get_by_id(tickettype_id)

    Agency_ticket_type = AgencyModel.query(
        AgencyModel.destination == TicketType_delete.travel.get().destination_start
    )

    count = 0
    for agency in Agency_ticket_type:
        count_ticket_created = TicketModel.query(
            TicketModel.type_name == TicketType_delete.type_name,
            TicketModel.class_name == TicketType_delete.class_name,
            TicketModel.journey_name == TicketType_delete.journey_name,
            TicketModel.agency == agency.key,
            TicketModel.selling == False
        ).count()
        if count_ticket_created >= 1:
            count += 1

    if count >= 1:
        data = json.dumps({
            'statut': 'OK'
        }, sort_keys=True)
    else:
        data = json.dumps({
            'statut': 'error'
        }, sort_keys=True)

    return data


#-------------------------------------------------------------------------------
#
# Class Type Controller
#
#-------------------------------------------------------------------------------

@app.route('/settings/tickettype/class', methods=['GET', 'POST'])
@app.route('/settings/tickettype/class/<int:class_type_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('admin', 'super_admin'))
def ClassType_Index(class_type_id=None):
    menu = 'settings'
    submenu = 'tickettype'

    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    feed = ActivityModel.query(
        ActivityModel.object == 'ClassTypeModel',
    ).order(
        -ActivityModel.time
    )

    feed_tab = []
    count = 0
    for feed in feed:
        feed_list = {}
        feed_list['user'] = feed.user_modify
        vess = ClassTypeModel.get_by_id(int(feed.identity))
        if vess:
            feed_list['data'] = str(vess.name)
        else:
            feed_list['data'] = feed.last_value
        feed_list['time'] = feed.time
        feed_list['nature'] = feed.nature
        feed_list['id'] = feed.identity
        feed_tab.append(feed_list)
        count += 1
        if count > 5 and not request.args.get('modal'):
            count += 1
            break

    if request.args.get('modal'):
        return render_template('/tickettype/all_feed_class.html', **locals())

    if class_type_id:
        class_type = ClassTypeModel.get_by_id(class_type_id)
        form = FormClassType(obj=class_type)
    else:
        class_type = ClassTypeModel()
        form = FormClassType(request.form)

    if form.validate_on_submit():
        class_exist = ClassTypeModel.query(ClassTypeModel.name == form.name.data).count()

        if class_exist >= 1:
            form.name.errors.append('This name '+str(form.name.data)+' exist')
        else:
            class_type.name = form.name.data
            class_type.put()

            activity = ActivityModel()
            activity.user_modify = current_user.key
            activity.identity = class_type.key.id()
            activity.object = "ClassTypeModel"
            activity.time = function.datetime_convert(date_auto_nows)

            if class_type_id:
                activity.nature = 4
                flash(u"Class Updated!", "success")

            else:
                activity.nature = 1
                flash(u"Class Saved!", "success")

            activity.put()
            return redirect(url_for('ClassType_Index'))

    class_type_list = ClassTypeModel.query()

    return render_template("/tickettype/index-class-type.html", **locals())

@app.route('/ClassType_Default/<int:class_type_id>')
@login_required
@roles_required(('admin', 'super_admin'))
def ClassType_Default(class_type_id):

    class_type = ClassTypeModel.get_by_id(class_type_id)

    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    activity = ActivityModel()
    activity.user_modify = current_user.key
    activity.identity = class_type.key.id()
    activity.object = "ClassTypeModel"
    activity.time = function.datetime_convert(date_auto_nows)

    if not class_type.default:
        journey_default_exist = ClassTypeModel.query(
            ClassTypeModel.default == True
        ).count()

        if journey_default_exist >= 1:
            flash(u"you can not define two class as a criterion 'is default'!", "danger")
        else:
            activity.nature = 6
            flash(u"Journey Updated!", "success")
            class_type.default = True

    else:
        activity.nature = 7
        flash(u"Journey Updated!", "success")
        class_type.default = False

    class_type.put()
    activity.put()
    return redirect(url_for('ClassType_Index'))


@app.route('/ClassType_Delete/<int:class_type_id>')
@login_required
@roles_required(('admin', 'super_admin'))
def ClassType_Delete(class_type_id):

    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    class_delete = ClassTypeModel.get_by_id(class_type_id)

    class_ticket_type_exist = TicketTypeModel.query(
        TicketTypeModel.class_name == class_delete.key
    ).count()

    from ..ticket.models_ticket import TicketModel
    class_ticket_exist = TicketModel.query(
        TicketModel.class_name == class_delete.key
    ).count()

    if class_ticket_type_exist >= 1 or class_ticket_exist >= 1:
        flash(u"You can't delete this class "+class_delete.name+u" it's used by ticket type and some ticket!", "danger")
        return redirect(url_for('ClassType_Index'))

    del_activity = ActivityModel.query(
            ActivityModel.object == "ClassTypeModel",
            ActivityModel.identity == class_delete.key.id()
    )

    for del_act in del_activity:
        del_act.key.delete()

    activity = ActivityModel()
    activity.user_modify = current_user.key
    activity.identity = class_delete.key.id()
    activity.object = "ClassTypeModel"
    activity.time = function.datetime_convert(date_auto_nows)
    activity.nature = 3
    activity.put()

    class_delete.key.delete()
    flash(u"Class has been deleted successfully!", "success")
    return redirect(url_for('ClassType_Index'))


#-------------------------------------------------------------------------------
#
# Journey Type Controller
#
#-------------------------------------------------------------------------------

@app.route('/settings/tickettype/journettype', methods=['GET', 'POST'])
@app.route('/settings/tickettype/journettype/<int:journey_type_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('admin', 'super_admin'))
def JourneyType_Index(journey_type_id=None):
    menu = 'settings'
    submenu = 'tickettype'

    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    feed = ActivityModel.query(
        ActivityModel.object == 'JourneyTypeModel',
    ).order(
        -ActivityModel.time
    )

    feed_tab = []
    count = 0
    for feed in feed:
        feed_list = {}
        feed_list['user'] = feed.user_modify
        vess = JourneyTypeModel.get_by_id(feed.identity)
        if vess:
            feed_list['data'] = vess.name
        else:
            feed_list['data'] = feed.last_value
        feed_list['time'] = feed.time
        feed_list['nature'] = feed.nature
        feed_list['id'] = feed.identity
        feed_tab.append(feed_list)
        count += 1
        if count > 5 and not request.args.get('modal'):
            count += 1
            break

    if request.args.get('modal'):
        return render_template('/tickettype/all_feed_journey.html', **locals())

    if journey_type_id:
        journey_type = JourneyTypeModel.get_by_id(journey_type_id)
        form = FormJourneyType(obj=journey_type)
    else:
        journey_type = JourneyTypeModel()
        form = FormJourneyType(request.form)

    if form.validate_on_submit():
        journey_exist = JourneyTypeModel.query(JourneyTypeModel.name == form.name.data).count()

        number_journey_type = JourneyTypeModel.query().count()

        if number_journey_type <= 2:
            if journey_exist >= 1:
                form.name.errors.append('This name '+str(form.name.data)+' exist')
            else:
                journey_type.name = form.name.data
                journey_type.put()

                activity = ActivityModel()
                activity.user_modify = current_user.key
                activity.identity = journey_type.key.id()
                activity.object = "JourneyTypeModel"
                activity.time = function.datetime_convert(date_auto_nows)

                if journey_type_id:
                    activity.nature = 4
                    flash(u"Journey Updated!", "success")

                else:
                    activity.nature = 1
                    flash(u"Journey Saved!", "success")

                activity.put()
                return redirect(url_for('JourneyType_Index'))
        else:
            flash(u"You can not create more than two journey!", "danger")

    journey_type_list = JourneyTypeModel.query()

    return render_template("/tickettype/index-journey-type.html", **locals())


@app.route('/JourneyType_Default/<int:journey_type_id>')
@login_required
@roles_required(('admin', 'super_admin'))
def JourneyType_Default(journey_type_id):

    journey_type = JourneyTypeModel.get_by_id(journey_type_id)

    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    activity = ActivityModel()
    activity.user_modify = current_user.key
    activity.identity = journey_type.key.id()
    activity.object = "JourneyTypeModel"
    activity.time = function.datetime_convert(date_auto_nows)

    if not journey_type.default:
        journey_default_exist = JourneyTypeModel.query(
            JourneyTypeModel.default == True
        ).count()

        if journey_default_exist >= 1:
            flash(u"you can not define two type of ticket as a criterion 'is default'!", "danger")
        else:
            activity.nature = 6
            flash(u"Journey Updated!", "success")
            journey_type.default = True
    else:
        activity.nature = 7
        flash(u"Journey Saved!", "success")
        journey_type.default = False

    journey_type.put()
    activity.put()

    return redirect(url_for('JourneyType_Index'))



@app.route('/JourneyType_retuned/<int:journey_type_id>')
@login_required
@roles_required(('admin', 'super_admin'))
def JourneyType_retuned(journey_type_id):

    journey_type = JourneyTypeModel.get_by_id(journey_type_id)

    if not journey_type.returned:
        journey_returned_exist = JourneyTypeModel.query(
            JourneyTypeModel.returned == True
        ).count()

        if journey_returned_exist >= 1:
            flash(u"you can not define two type of ticket as a criterion 'Used to return the tickets'!", "danger")
        else:
            flash(u"Journey Updated!", "success")
            journey_type.returned = True
    else:

        journey_used_ticket_type = TicketTypeModel.query(
            TicketTypeModel.journey_name == journey_type.key
        ).count()

        from ..ticket.models_ticket import TicketModel
        journey_used_ticket = TicketModel.query(
            TicketModel.journey_name == journey_type.key
        ).count()

        if journey_used_ticket >= 1 or journey_used_ticket_type >= 1:

            flash(u"you can not disabled the return function for this journey", "danger")

        else:
            flash(u"Journey Updated!", "success")
            journey_type.returned = False

    journey_type.put()

    return redirect(url_for('JourneyType_Index'))


@app.route('/JourneyType_Delete/<int:journey_type_id>')
@login_required
@roles_required(('admin', 'super_admin'))
def JourneyType_Delete(journey_type_id):

    journey_delete = JourneyTypeModel.get_by_id(journey_type_id)

    journey_ticket_type_exist = TicketTypeModel.query(
        TicketTypeModel.journey_name == journey_delete.key
    ).count()

    from ..ticket.models_ticket import TicketModel
    journey_ticket_exist = TicketModel.query(
        TicketModel.journey_name == journey_delete.key
    ).count()

    if journey_ticket_exist >= 1 or journey_ticket_type_exist >= 1:
        flash(u"You can't delete this journey :"+journey_delete.name+u" it's used by ticket type and some ticket!!", "danger")
        return redirect(url_for('JourneyType_Index'))

    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    del_activity = ActivityModel.query(
            ActivityModel.object == "JourneyTypeModel",
            ActivityModel.identity == journey_delete.key.id()
    )

    for del_act in del_activity:
        del_act.key.delete()

    activity = ActivityModel()
    activity.user_modify = current_user.key
    activity.identity = journey_delete.key.id()
    activity.object = "JourneyTypeModel"
    activity.time = function.datetime_convert(date_auto_nows)
    activity.nature = 3
    activity.put()

    journey_delete.key.delete()
    flash(u"Journey has been deleted successfully!", "success")
    return redirect(url_for('JourneyType_Index'))


#-------------------------------------------------------------------------------
#
# Ticket Type Name Controller
#
#-------------------------------------------------------------------------------

@app.route("/settings/ticket/category", methods=['GET', 'POST'])
@app.route('/settings/ticket/category/<int:ticket_type_name_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('admin', 'super_admin'))
def Ticket_Type_Name_Index(ticket_type_name_id=None):
    menu = 'settings'
    submenu = 'tickettype'

    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    feed = ActivityModel.query(
        ActivityModel.object == 'TicketTypeNameModel',
    ).order(
        -ActivityModel.time
    )

    feed_tab = []
    count = 0
    for feed in feed:
        feed_list = {}
        feed_list['user'] = feed.user_modify
        vess = TicketTypeNameModel.get_by_id(feed.identity)
        if vess:
            feed_list['data'] = vess.name
        else:
            feed_list['data'] = feed.last_value
        feed_list['time'] = feed.time
        feed_list['nature'] = feed.nature
        feed_list['id'] = feed.identity
        feed_tab.append(feed_list)
        count += 1
        if count > 5 and not request.args.get('modal'):
            count += 1
            break

    if request.args.get('modal'):
        return render_template('/tickettype/all_feed_catetory.html', **locals())

    if ticket_type_name_id:
        tickets = TicketTypeNameModel.get_by_id(ticket_type_name_id)
        form = FormTicketTypeName(obj=tickets)
    else:
        tickets = TicketTypeNameModel()
        form = FormTicketTypeName()

    if form.validate_on_submit():
        ticket_exist = TicketTypeNameModel.query(TicketTypeNameModel.name == form.name.data).count()

        number_ticket_normal = TicketTypeNameModel.query(
            TicketTypeNameModel.special == False
        ).count()

        if ticket_exist >= 1:
            form.name.errors.append('This name '+str(form.name.data)+' exist')
        else:
            tickets.name = form.name.data

            activity = ActivityModel()

            activity.user_modify = current_user.key
            activity.object = "TicketTypeNameModel"
            activity.time = function.datetime_convert(date_auto_nows)

            if number_ticket_normal >= 2:
                tickets.special = True

            this_ticket = tickets.put()
            if ticket_type_name_id:
                activity.nature = 4
                flash(u"Category Updated!", "success")

            else:
                activity.nature = 1
                flash(u"Category Saved!", "success")

            activity.identity = this_ticket.id()
            activity.put()
            return redirect(url_for('Ticket_Type_Name_Index'))


    ticket_list = TicketTypeNameModel.query()

    return render_template("/tickettype/index-ticket-type-name.html", **locals())


@app.route("/Ticket_Type_Name_Child/<int:ticket_type_name_id>", methods=["GET", "POST"])
@login_required
@roles_required(('admin', 'super_admin'))
def Ticket_Type_Name_Child(ticket_type_name_id):
    ticket = TicketTypeNameModel.get_by_id(ticket_type_name_id)

    if not ticket.is_child:
        is_child_exist = TicketTypeNameModel.query(
            TicketTypeNameModel.is_child == True,
            TicketTypeNameModel.key != ticket.key
        ).count()
        if is_child_exist >= 1:
            flash(u"you can not define two type of ticket as a criterion 'is child'!", "danger")
        else:
            ticket.is_child = True
    else:
        ticket.is_child = False
    ticket.put()

    return redirect(url_for("Ticket_Type_Name_Index"))


@app.route("/Ticket_Type_Name_Default/<int:ticket_type_name_id>")
@login_required
@roles_required(('admin', 'super_admin'))
def Ticket_Type_Name_Default(ticket_type_name_id):

    ticket = TicketTypeNameModel.get_by_id(ticket_type_name_id)
    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    activity = ActivityModel()
    activity.user_modify = current_user.key
    activity.object = "TicketTypeNameModel"
    activity.time = function.datetime_convert(date_auto_nows)
    activity.identity = ticket.key.id()

    if not ticket.default:
        is_default_exist = TicketTypeNameModel.query(
            TicketTypeNameModel.default == True,
            TicketTypeNameModel.key != ticket.key
        ).count()

        if is_default_exist >= 1:
            flash(u"you can not define two type of ticket as a criterion 'is default'!", "danger")
        else:
            activity.nature = 6
            flash(u"Category Updated!", "success")
            ticket.default = True
    else:
        activity.nature = 7
        flash(u"Category Updated!", "success")
        ticket.default = False

    ticket.put()
    activity.put()
    return redirect(url_for("Ticket_Type_Name_Index"))


@app.route("/Ticket_Type_Name_Special/<int:ticket_type_name_id>")
@login_required
@roles_required(('admin', 'super_admin'))
def Ticket_Type_Name_Special(ticket_type_name_id):

    ticket = TicketTypeNameModel.get_by_id(ticket_type_name_id)

    ticket = TicketTypeNameModel.get_by_id(ticket_type_name_id)

    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    activity = ActivityModel()
    activity.user_modify = current_user.key
    activity.object = "TicketTypeNameModel"
    activity.time = function.datetime_convert(date_auto_nows)
    activity.identity = ticket.key.id()

    if ticket.special:
        number_ticket_normal = TicketTypeNameModel.query(
            TicketTypeNameModel.special == False
        ).count()
        if number_ticket_normal >= 2:
            flash(u"You can not activate more than two normal ticket type", "danger")
        else:
            activity.nature = 9
            flash(u"Category Updated!", "success")
            ticket.special = False
    else:
        activity.nature = 8
        flash(u"Category Updated!", "success")
        ticket.special = True

    activity.put()
    ticket.put()
    return redirect(url_for("Ticket_Type_Name_Index"))


@app.route("/Delete_Ticket_Type_Name/<int:ticket_type_name_id>")
@login_required
@roles_required(('admin', 'super_admin'))
def Delete_Ticket_Type_Name(ticket_type_name_id):

    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    delete_ticket = TicketTypeNameModel.get_by_id(ticket_type_name_id)
    # On verifiera si le TicketTypeName est utilisee

    ticket_type_name_ticket_type_exist = TicketTypeModel.query(
        TicketTypeModel.type_name == delete_ticket.key
    ).count()

    from ..ticket.models_ticket import TicketModel
    ticket_type_name_ticket_exist = TicketModel.query(
        TicketModel.type_name == delete_ticket.key
    ).count()

    if ticket_type_name_ticket_exist >= 1 or ticket_type_name_ticket_type_exist >= 1:
        flash(u"You can't delete this Catetory :"+delete_ticket.name+u" it's used by ticket type and some ticket!!", "danger")
        return redirect(url_for("Ticket_Type_Name_Index"))

    del_activity = ActivityModel.query(
            ActivityModel.object == "TicketTypeNameModel",
            ActivityModel.identity == delete_ticket.key.id()
    )

    for del_act in del_activity:
        del_act.key.delete()

    activity = ActivityModel()
    activity.user_modify = current_user.key
    activity.object = "TicketTypeNameModel"
    activity.time = function.datetime_convert(date_auto_nows)
    activity.identity = delete_ticket.key.id()
    activity.nature = 3
    activity.put()

    # Si oui il ne sera pas supprime
    delete_ticket.key.delete()
    flash(u"Catetory has been deleted successfully!", "success")
    return redirect(url_for("Ticket_Type_Name_Index"))
