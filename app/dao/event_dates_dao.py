from app import db
from app.dao.decorators import transactional
from app.models import EventDate


@transactional
def dao_create_event_date(event_date, speakers=None):
    if speakers:
        for s in speakers:
            event_date.speakers.append(s)

    db.session.add(event_date)


@transactional
def dao_delete_event_date(event_date_id):
    event_date = EventDate.query.filter_by(id=event_date_id).one()
    db.session.delete(event_date)


@transactional
def dao_update_event_date(event_date_id, **kwargs):
    return EventDate.query.filter_by(id=event_date_id).update(
        kwargs
    )


def dao_get_event_dates():
    return EventDate.query.order_by(EventDate.event_datetime).all()


def dao_get_event_date_by_id(event_date_id):
    return EventDate.query.filter_by(id=event_date_id).one()


def dao_has_event_id_and_datetime(event_id, datetime):
    return EventDate.query.filter_by(
        event_id=event_id, event_datetime=datetime).first() != None  # noqa E711 SqlAlchemy syntax
