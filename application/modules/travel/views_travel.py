__author__ = 'wilrona'

from ...modules import *

from models_travel import TravelModel, DestinationModel

from forms_travel import FormTravel
# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route('/settings/travel')
@login_required
@roles_required(('super_admin', 'admin'))
def Travel_Index():
    menu = 'settings'
    submenu = 'travel'

    travels = TravelModel.query()

    from ..activity.models_activity import ActivityModel
    feed = ActivityModel.query(
        ActivityModel.object == 'TravelModel',
    ).order(
        -ActivityModel.time
    )

    feed_tab = []
    count = 0
    for feed in feed:
        feed_list = {}
        feed_list['user'] = feed.user_modify
        vess = TravelModel.get_by_id(feed.identity)
        feed_list['data'] = vess.destination_start.get().name+" - "+vess.destination_check.get().name+"("+str(function.format_date(vess.time, "%H:%M"))+")"
        feed_list['time'] = feed.time
        feed_list['nature'] = feed.nature
        feed_list['id'] = feed.identity
        feed_tab.append(feed_list)
        count += 1
        if count > 5 and not request.args.get('modal'):
            count += 1
            break

    if request.args.get('modal'):
        return render_template('/travel/all_feed.html', **locals())

    return render_template('/travel/index.html', **locals())


@app.route('/settings/travel/edit', methods=['GET', 'POST'])
@app.route('/settings/travel/edit/<int:travel_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('super_admin', 'admin'))
def Travel_Edit(travel_id=None):
    menu = 'settings'
    submenu = 'travel'

    from ..activity.models_activity import ActivityModel

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    destitravel = DestinationModel.query()
    feed_tab = []
    if travel_id:
        travelmod = TravelModel.get_by_id(travel_id)
        form = FormTravel(obj=travelmod)

        form.destination_start.data = travelmod.destination_start.get().key.id()
        form.destination_check.data = travelmod.destination_check.get().key.id()

        feed = ActivityModel.query(
            ActivityModel.object == 'TravelModel',
            ActivityModel.identity == travelmod.key.id()
        ).order(
            -ActivityModel.time
        )
        count = 0
        for feed in feed:
            feed_list = {}
            feed_list['user'] = feed.user_modify
            vess = TravelModel.get_by_id(feed.identity)
            feed_list['data'] = feed.last_value
            if vess:
                feed_list['data'] = vess.destination_start.get().name+" - "+vess.destination_check.get().name+"("+str(function.format_date(vess.time, "%H:%M"))+")"
            feed_list['time'] = feed.time
            feed_list['nature'] = feed.nature
            feed_list['id'] = feed.identity
            feed_tab.append(feed_list)
            count += 1
            if count > 5:
                count += 1
                break
    else:
        travelmod = TravelModel()
        form = FormTravel(request.form)

    if form.validate_on_submit():
        start_destitravel = DestinationModel.get_by_id(int(form.destination_start.data))
        check_destitravel = DestinationModel.get_by_id(int(form.destination_check.data))

        # on compte le nombre de travel ayant la meme destination depart et arrive
        count_dest_travel = TravelModel.query(
            TravelModel.destination_start == start_destitravel.key,
            TravelModel.destination_check == check_destitravel.key
        ).count()

        if count_dest_travel >= 1:
            if travelmod.destination_start == start_destitravel.key and travelmod.destination_check == check_destitravel.key:
                activity = ActivityModel()
                activity.last_value = str(travelmod.time)

                travelmod.time = function.time_convert(form.time.data)
                this_travel = travelmod.put()


                activity.user_modify = current_user.key
                activity.object = "TravelModel"
                activity.time = function.datetime_convert(date_auto_nows)
                activity.identity = this_travel.id()
                activity.nature = 4
                activity.put()

                flash(u' Travel Updated! ', 'success')
                return redirect(url_for("Travel_Index"))

            else:
                flash(u"This travel exist!", "danger")

        elif start_destitravel == check_destitravel:
            flash(u"This travel kind  does'nt exist!", "danger")

        else:
            activity_1 = ActivityModel()
            activity_1.last_value = str(travelmod.time)

            if form.time.data:
                travelmod.time = function.time_convert(form.time.data)
            travelmod.destination_start = start_destitravel.key
            travelmod.destination_check = check_destitravel.key

            if not travel_id:
                travelmod.datecreate = function.datetime_convert(date_auto_nows)

            if not travel_id:
                travelmod2 = TravelModel()
                if form.time.data:
                    travelmod2.time = function.time_convert(form.time.data)
                travelmod2.destination_start = check_destitravel.key
                travelmod2.destination_check = start_destitravel.key
                travelmod2.datecreate = function.datetime_convert(date_auto_nows)
                this_travel_2 = travelmod2.put()

                activity = ActivityModel()
                activity.user_modify = current_user.key
                activity.object = "TravelModel"
                activity.time = function.datetime_convert(date_auto_nows)
                activity.identity = this_travel_2.id()
                activity.nature = 1
                activity.put()


            this_travel = travelmod.put()

            activity_1.user_modify = current_user.key
            activity_1.object = "TravelModel"
            activity_1.time = function.datetime_convert(date_auto_nows)
            activity_1.identity = this_travel.id()
            activity_1.nature = 1
            activity_1.put()

            flash(u' Travel Saved! ', 'success')
            return redirect(url_for("Travel_Index"))

    return render_template('/travel/edit.html', **locals())