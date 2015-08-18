__author__ = 'wilrona'


from ...modules import *

from models_departure import DepartureModel, VesselModel, TravelModel
from forms_departure import FormDeparture
# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route('/manage/journey')
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Departure_Index():
    menu = 'recording'
    submenu = 'departure'

    if not current_user.has_roles(('admin', 'super_admin')) and current_user.has_roles('manager_agency'):
        from ..agency.models_agency import AgencyModel
        agency_user = AgencyModel.get_by_id(int(session.get('agence_id_local')))
        return redirect(url_for('Departure_manager_agency', agency_id=agency_user.key.id()))

    year = datetime.date.today().year

    day_today = datetime.date.today().day
    month_today = datetime.date.today().month
    date_day = datetime.date(year, month_today, day_today)

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    time_now = function.datetime_convert(date_auto_nows).time()

    departures = DepartureModel.query().order(
        DepartureModel.departure_date,
        DepartureModel.schedule,
        DepartureModel.time_delay
    )

    return render_template('/departure/index.html', **locals())


@app.route('/Departure_manager_agency/<int:agency_id>')
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Departure_manager_agency(agency_id):
    menu = 'recording'
    submenu = 'departure'

    year = datetime.date.today().year

    day_today = datetime.date.today().day
    month_today = datetime.date.today().month
    date_day = datetime.date(year, month_today, day_today)

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    time_now = function.datetime_convert(date_auto_nows).time()

    from ..agency.models_agency import AgencyModel
    user_agency_id = AgencyModel.get_by_id(agency_id)

    departure_local_query = DepartureModel.query()

    departure_locals = []
    departure_in_commings = []
    foreign_departures = []
    for departure_local_loop in departure_local_query:
        if departure_local_loop.destination.get().destination_start == user_agency_id.destination:
            departure_locals.append(departure_local_loop)
        if departure_local_loop.destination.get().destination_check == user_agency_id.destination:
            departure_in_commings.append(departure_local_loop)
        if departure_local_loop.destination.get().destination_check != user_agency_id.destination and departure_local_loop.destination.get().destination_start != user_agency_id.destination:
            foreign_departures.append(departure_local_loop)

    return render_template('/departure/index_manager_agency.html', **locals())

