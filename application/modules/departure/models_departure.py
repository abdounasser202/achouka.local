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
