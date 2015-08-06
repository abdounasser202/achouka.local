__author__ = 'wilrona'

from ...modules import *

from models_destination import DestinationModel, CurrencyModel
from forms_destination import FormDestination

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route('/settings/destination')
@login_required
@roles_required(('admin', 'super_admin'))
def Destination_Index():
    menu = 'settings'
    submenu = 'destination'

    destinations = DestinationModel.query()

    from ..activity.models_activity import ActivityModel
    feed = ActivityModel.query(
        ActivityModel.object == 'DestinationModel',
    ).order(
        -ActivityModel.time
    )

    feed_tab = []
    count = 0
    for feed in feed:
        feed_list = {}
        feed_list['user'] = feed.user_modify
        vess = DestinationModel.get_by_id(feed.identity)
        if vess:
            feed_list['data'] = vess.name+" ("+str(vess.code)+")"
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
        return render_template('/destination/all_feed.html', **locals())

    return render_template('/destination/index.html', **locals())


@app.route('/settings/destination/Edit/<int:destination_id>', methods=['GET', 'POST'])
@app.route('/settings/destination/Edit', methods=['GET', 'POST'])
@login_required
@roles_required(('admin', 'super_admin'))
def Destination_Edit(destination_id=None):
    menu = 'settings'
    submenu = 'destination'

    from ..activity.models_activity import ActivityModel
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")


    #liste des devises
    listcurency = CurrencyModel.query()

    feed_tab = []

    if destination_id:
        # formulaire et information de la devise a editer
        destination = DestinationModel.get_by_id(destination_id)
        form = FormDestination(obj=destination)

        from ..agency.models_agency import AgencyModel
        from ..travel.models_travel import TravelModel
        from ..transaction.models_transaction import TransactionModel

        agency_destination_exist = AgencyModel.query(
            AgencyModel.destination == destination.key
        ).count()

        travel_destination_start_exist = TravelModel.query(
            TravelModel.destination_start == destination.key
        ).count()

        travel_destination_check_exist = TravelModel.query(
            TravelModel.destination_check == destination.key
        ).count()

        transaction_destination_exist = TransactionModel.query(
            TransactionModel.destination == destination.key
        ).count()

        currency_destination_id = destination.currency.get().key.id()

        feed = ActivityModel.query(
            ActivityModel.object == 'DestinationModel',
            ActivityModel.identity == destination.key.id()
        ).order(
            -ActivityModel.time
        )
        count = 0
        for feed in feed:
            feed_list = {}
            feed_list['user'] = feed.user_modify
            vess = DestinationModel.get_by_id(feed.identity)
            feed_list['data'] = feed.last_value
            if vess:
                feed_list['data'] = vess.name+" ("+str(vess.code)+")"
            feed_list['time'] = feed.time
            feed_list['nature'] = feed.nature
            feed_list['id'] = feed.identity
            feed_tab.append(feed_list)
            count += 1
            if count > 5:
                count += 1
                break

    else:
        form = FormDestination()
        destination = DestinationModel()
        agency_destination_exist = 0
        travel_destination_check_exist = 0
        travel_destination_start_exist = 0
        transaction_destination_exist = 0

    if form.validate_on_submit():
        currency_dest = CurrencyModel.get_by_id(int(form.currency.data))
        dest_exit = DestinationModel.query(DestinationModel.code == form.code.data).count()
        if dest_exit >= 1:
            if destination.code == form.code.data and destination_id: #Traitement pour la mise a jour
                destination.code = form.code.data
                destination.name = form.name.data
                destination.currency = currency_dest.key

                this_destination = destination.put()

                # enregistrement de l'activite de modification
                activity = ActivityModel()
                activity.user_modify = current_user.key
                activity.identity = this_destination.id()
                activity.nature = 4
                activity.object = "DestinationModel"
                activity.time = function.datetime_convert(date_auto_nows)
                activity.put()

                flash(u' Destination Update. ', 'success')
                return redirect(url_for('Destination_Index'))

            else:
                form.code.errors.append('Other destination use this code '+form.code.data)
        else:
            destination.code = form.code.data
            destination.name = form.name.data
            destination.currency = currency_dest.key

            this_destination = destination.put()

            # enregistrement de l'activite de creation
            activity = ActivityModel()
            activity.user_modify = current_user.key
            activity.identity = this_destination.id()
            activity.time = function.datetime_convert(date_auto_nows)
            activity.object = "DestinationModel"

            if destination_id:
                activity.nature = 4
                flash(u' Destination Update. ', 'success')
            else:
                activity.nature = 1
                flash(u' Destination Save. ', 'success')

            activity.put()
            return redirect(url_for('Destination_Index'))

    return render_template('/destination/edit.html', **locals())


@app.route('/settings/destination/delete/', methods=['GET', 'POST'])
@app.route('/settings/destination/delete/<int:destination_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('admin', 'super_admin'))
def Destination_Delete(destination_id=None):
    menu = 'settings'
    submenu = 'vessel'

    delete_destination = DestinationModel.get_by_id(int(destination_id))

    from ..agency.models_agency import AgencyModel
    from ..travel.models_travel import TravelModel
    from ..transaction.models_transaction import TransactionModel
    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    agency_destination_exist = AgencyModel.query(
        AgencyModel.destination == delete_destination.key
    ).count()

    travel_destination_start_exist = TravelModel.query(
        TravelModel.destination_start == delete_destination.key
    ).count()

    travel_destination_check_exist = TravelModel.query(
        TravelModel.destination_check == delete_destination.key
    ).count()

    transaction_destination_exist = TransactionModel.query(
        TransactionModel.destination == delete_destination.key
    ).count()

    if agency_destination_exist >= 1 or travel_destination_start_exist >= 1 or travel_destination_check_exist >= 1 or transaction_destination_exist >= 1:
        flash(u'You can\'t delete this destination', 'danger')
        return redirect(url_for("Destination_Index"))

    else:

        del_activity = ActivityModel.query(
            ActivityModel.object == "DestinationModel",
            ActivityModel.identity == delete_destination.key.id()
        )

        for del_act in del_activity:
            del_act.key.delete()

        activity = ActivityModel()
        activity.user_modify = current_user.key
        activity.identity = delete_destination.key.id()
        activity.nature = 3
        activity.object = "DestinationModel"
        activity.time = function.datetime_convert(date_auto_nows)
        activity.put()

        delete_destination.key.delete()
        flash(u'Destination has been deleted successfully', 'success')
        return  redirect(url_for("Destination_Index"))

    return render_template('/destination/index.html', **locals())

