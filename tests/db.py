from app import db

from app.dao.events_dao import dao_create_event
from app.dao.event_types_dao import dao_create_event_type
from app.dao.fees_dao import dao_create_fee
from app.models import Event, EventType, Fee


def create_event(title='test title', description='test description'):
    data = {
        'title': title,
        'description': description,
    }
    event = Event(**data)

    dao_create_event(event)
    return event


def create_event_type(
        old_id=1,
        event_type='talk',
        event_desc='test talk',
        event_filename=None,
        duration=45,
        repeat=1,
        repeat_interval=0
):
    data = {
        'old_id': old_id,
        'event_type': event_type,
        'event_desc': event_desc,
        'event_filename': event_filename,
        'duration': duration,
        'repeat': repeat,
        'repeat_interval': repeat_interval
    }
    event_type = EventType(**data)

    dao_create_event_type(event_type)
    return event_type


def create_fee(event_type_id=None, fee=5, conc_fee=3, multi_day_fee=0, multi_day_conc_fee=0, valid_from='2017-08-31'):
    if not event_type_id:
        event_type = create_event_type()
        event_type_id = event_type.id

    data = {
        'event_type_id': event_type_id,
        'fee': fee,
        'conc_fee': conc_fee,
        'multi_day_fee': multi_day_fee,
        'multi_day_conc_fee': multi_day_conc_fee,
        'valid_from': valid_from
    }
    fee = Fee(**data)

    dao_create_fee(fee)
    return fee
