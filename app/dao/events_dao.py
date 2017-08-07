from app import db
from app.dao.decorators import transactional
from app.models import Event


@transactional
def dao_create_event(event):
    db.session.add(event)


@transactional
def dao_update_event(event, **kwargs):
    for key, value in kwargs.items():
        setattr(event, key, value)
    db.session.add(event)


def dao_get_events():
    return Event.query.order_by(Event.id).all()
