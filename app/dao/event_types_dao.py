from app import db
from app.dao.decorators import transactional
from app.models import EventType


@transactional
def dao_create_event_type(event_type):
    db.session.add(event_type)


@transactional
def dao_update_event_type(event_type_id, **kwargs):
    return EventType.query.filter_by(id=event_type_id).update(
        kwargs
    )


def dao_get_event_types():
    return EventType.query.order_by(EventType.event_type).all()


def dao_get_event_type_by_id(event_type_id):
    return EventType.query.filter_by(id=event_type_id).one()


def dao_get_event_type_by_old_id(old_event_type_id):
    return EventType.query.filter_by(old_id=old_event_type_id).one()
