from app import db
from app.dao.decorators import transactional
from app.models import EventType


@transactional
def dao_create_event_type(event_type):
    db.session.add(event_type)


@transactional
def dao_update_event_type(event_type_obj, **kwargs):
    for key, value in kwargs.items():
        setattr(event_type_obj, key, value)
    db.session.add(event_type_obj)


def dao_get_event_types():
    return EventType.query.order_by(EventType.id).all()
