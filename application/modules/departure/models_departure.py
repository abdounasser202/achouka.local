__author__ = 'wilrona'

from google.appengine.ext import ndb
from ..travel.models_travel import TravelModel
from ..vessel.models_vessel import VesselModel


class DepartureModel(ndb.Model):
    departure_date = ndb.DateProperty()
    schedule = ndb.TimeProperty()
    time_delay = ndb.TimeProperty()
    destination = ndb.KeyProperty(kind=TravelModel)
    vessel = ndb.KeyProperty(kind=VesselModel)
    date_update = ndb.DateProperty(auto_now=True)

    def make_to_dict(self):
        to_dict = {}
        to_dict['departure_id'] = self.key.id()
        to_dict['departure_date'] = str(self.departure_date)
        to_dict['departure_schedule'] = str(self.schedule)
        if self.time_delay:
            to_dict['departure_delay'] = str(self.time_delay)
            to_dict['delay'] = True
        else:
            to_dict['delay'] = False
        to_dict['departure_destination'] = self.destination.id()
        to_dict['departure_vessel'] = self.vessel.id()
        return to_dict

    def reserved(self):
        from ..ticket.models_ticket import TicketModel

        reserved_count = TicketModel.query(
            TicketModel.departure == self.key,
            TicketModel.travel_ticket == self.destination
        ).count()

        reserved = False
        if reserved_count >= 1:
            reserved = True

        return reserved
