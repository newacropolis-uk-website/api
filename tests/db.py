from app import db

from app.dao.events_dao import dao_create_event
from app.models import Event


def create_event(title='test title', description='test description', date='2017-08-07 12:00:00'):
    data = {
        'title': title,
        'description': description,
        'date': date
    }
    event = Event(**data)

    dao_create_event(event)
    return event
