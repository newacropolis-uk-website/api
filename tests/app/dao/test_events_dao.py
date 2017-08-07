from app.dao.events_dao import dao_create_event, dao_update_event, dao_get_events
from app.models import Event

from tests.db import create_event


class WhenUsingEventDAO(object):

    def it_creates_an_event(self, db, db_session):
        event = create_event()

        assert Event.query.count() == 1
        event_from_db = Event.query.first()
        assert event == event_from_db

    def it_updates_an_event(self, db, db_session, sample_events):
        event = sample_events[0]
        dao_update_event(event, title='new title')

        event_from_db = Event.query.filter(Event.id == event.id).first()

        assert event.title == event_from_db.title

    def it_gets_all_event(self, db, db_session, sample_events):
        events = dao_get_events()

        assert Event.query.count() == len(sample_events)
        event_from_db = Event.query.all()
        assert set(events) == set(event_from_db)
