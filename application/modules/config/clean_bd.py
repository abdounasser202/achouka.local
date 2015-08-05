__author__ = 'Vercossa'


def clean_vessel():
    from ..vessel.models_vessel import VesselModel
    from ..departure.models_departure import DepartureModel

    vessel_list = VesselModel.query()

    for vessel in vessel_list:
        departure_vessel = DepartureModel.query(
            DepartureModel.vessel == vessel.key
        ).count()

        if not departure_vessel:
            vessel.key.delete()


def clean_currency():
    from ..currency.models_currency import CurrencyModel
    from ..ticket.models_ticket import TicketModel
    from ..ticket_type.models_ticket_type import TicketTypeModel

    currency_list = CurrencyModel.query()

    for currency in currency_list:

        tickettype_currency = TicketTypeModel.query(
            TicketTypeModel.currency == currency.key
        ).count()

        ticket_currency = TicketModel.query(
            TicketModel.sellpriceAgCurrency == currency.key
        ).count()

        ticket_currency_2 = TicketModel.query(
            TicketModel.sellpriceCurrency == currency.key
        ).count()

        if not ticket_currency and not ticket_currency_2 and not tickettype_currency:
            currency.key.delete()


def clean_destination():
    from ..agency.models_agency import AgencyModel
    from ..travel.models_travel import TravelModel, DestinationModel
    from ..transaction.models_transaction import TransactionModel

    destination_list = DestinationModel.query()

    for destination in destination_list:

        agency_destination = AgencyModel.query(
            AgencyModel.destination == destination.key
        ).count()

        travel_destination_start = TravelModel.query(
            TravelModel.destination_start == destination.key
        ).count()

        travel_destination_check = TravelModel.query(
            TravelModel.destination_check == destination.key
        ).count()

        transaction_destination = TransactionModel.query(
            TransactionModel.destination == destination.key
        ).count()

        if not agency_destination and not transaction_destination and not travel_destination_check and not travel_destination_start:
            destination.key.delete()


def clean_class():
    from ..ticket_type.models_ticket_type import ClassTypeModel, TicketTypeModel
    from ..ticket.models_ticket import TicketModel

    class_list = ClassTypeModel.query()

    for classe in class_list:

        tickettype = TicketTypeModel.query(
            TicketTypeModel.class_name == classe.key
        ).count()

        ticket = TicketModel.query(
            TicketModel.class_name == classe.key
        ).count()

        if not ticket and not tickettype:
            classe.key.delete()


def clean_journey():
    from ..ticket_type.models_ticket_type import JourneyTypeModel, TicketTypeModel
    from ..ticket.models_ticket import TicketModel

    journey_list = JourneyTypeModel.query()

    for journey in journey_list:

        tickettype = TicketTypeModel.query(
            TicketTypeModel.journey_name == journey.key
        ).count()

        ticket = TicketModel.query(
            TicketModel.journey_name == journey.key
        ).count()

        if not ticket and not tickettype:
            journey.key.delete()


def clean_categpry():
    from ..ticket_type.models_ticket_type import TicketTypeNameModel, TicketTypeModel
    from ..ticket.models_ticket import TicketModel

    category_list = TicketTypeNameModel.query()

    for category in category_list:

        tickettype = TicketTypeModel.query(
            TicketTypeModel.type_name == category.key
        ).count()

        ticket = TicketModel.query(
            TicketModel.type_name == category.key
        ).count()

        if not ticket and not tickettype:
            category.key.delete()

def clean_ticket():
    from ..ticket_type.models_ticket_type import TicketTypeModel

    tickettype_list = TicketTypeModel.query(
        TicketTypeModel.active == False
    )

    for tickettype in tickettype_list:
        tickettype.key.delete()






