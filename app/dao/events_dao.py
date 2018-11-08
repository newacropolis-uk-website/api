from datetime import datetime

from app import db
from app.dao.decorators import transactional
from app.models import Event, EventDate


@transactional
def dao_create_event(event):
    db.session.add(event)


@transactional
def dao_update_event(event_id, **kwargs):
    return Event.query.filter_by(id=event_id).update(
        kwargs
    )


def dao_get_events():
    return Event.query.order_by(Event.id).all()


def dao_get_future_events():
    return Event.query.join(EventDate).filter(
        EventDate.event_datetime > datetime.utcnow()
    ).order_by(Event.id).all()
