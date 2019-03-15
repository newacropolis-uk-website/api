from datetime import datetime, timedelta

from sqlalchemy import and_

from app import db
from app.dao.decorators import transactional
from app.models import Event, EventDate


@transactional
def dao_create_event(event):
    db.session.add(event)


@transactional
def dao_delete_event(event_id):
    event = Event.query.filter_by(id=event_id).one()
    db.session.delete(event)


@transactional
def dao_update_event(event_id, **kwargs):
    print(kwargs)
    return Event.query.filter_by(id=event_id).update(
        kwargs
    )


def dao_get_events():
    return Event.query.order_by(Event.id).all()


def dao_get_event_by_id(event_id):
    return Event.query.filter(Event.id == event_id).one()


def dao_get_events_in_year(year):
    return Event.query.filter(
        and_(
            EventDate.event_datetime >= "{}-01-01".format(year),
            EventDate.event_datetime < "{}-01-01".format(year + 1)
        )
    ).join(Event.event_dates).order_by(EventDate.event_datetime).all()


def dao_get_limited_events(num):
    return Event.query.join(
        Event.event_dates).order_by(
            EventDate.event_datetime.desc(), EventDate.event_datetime.desc()).limit(num).all()


def dao_get_future_events():
    return Event.query.join(EventDate).filter(
        EventDate.event_datetime >= datetime.today()
    ).order_by(Event.id).all()


def dao_get_past_year_events():
    return Event.query.filter(
        and_(
            EventDate.event_datetime < datetime.today(),
            EventDate.event_datetime > datetime.today() - timedelta(days=365)
        )
    ).join(Event.event_dates).order_by(EventDate.event_datetime).all()
