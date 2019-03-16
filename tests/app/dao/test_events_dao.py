from freezegun import freeze_time

from app.dao.events_dao import (
    dao_create_event,
    dao_delete_event,
    dao_update_event,
    dao_get_event,
    dao_get_events,
    dao_get_events_in_year,
    dao_get_future_events,
    dao_get_limited_events,
    dao_get_past_year_events,
)
from app.models import Event

from tests.db import create_event, create_event_date


class WhenUsingEventsDAO(object):

    def it_creates_an_event(self, db, db_session):
        event = create_event()

        assert Event.query.count() == 1
        event_from_db = Event.query.first()
        assert event == event_from_db

    def it_deletes_an_event(self, db, db_session):
        event = create_event()

        assert Event.query.count() == 1

        dao_delete_event(event.id)

        assert Event.query.count() == 0

    def it_creates_an_event_with_event_dates(self, db, db_session):
        event_date = create_event_date()
        event = create_event(event_dates=[event_date])

        assert Event.query.count() == 1
        event_from_db = Event.query.first()
        assert event == event_from_db
        assert event_from_db.event_dates[0] == event_date

    def it_deletes_an_event_with_event_dates(self, db, db_session):
        event_date = create_event_date()
        event = create_event(event_dates=[event_date])

        assert Event.query.count() == 1

        dao_delete_event(event.id)

        assert Event.query.count() == 0

    def it_updates_an_event_dao(self, db, db_session, sample_event):
        dao_update_event(sample_event.id, title='new title')

        event_from_db = Event.query.filter(Event.id == sample_event.id).first()

        assert sample_event.title == event_from_db.title

    def it_gets_all_events(self, db, db_session, sample_event, sample_event_type):
        events = [create_event(title='test title 2', event_type_id=sample_event_type.id), sample_event]
        events_from_db = dao_get_events()

        assert Event.query.count() == 2
        assert set(events) == set(events_from_db)

    def it_gets_an_event(self, db, db_session, sample_event):
        event = dao_get_event(sample_event.id)

        assert event == sample_event

    @freeze_time("2018-01-10T19:00:00")
    def it_gets_all_future_events(self, db, db_session, sample_event_with_dates, sample_event_type):
        event = create_event(
            title='future event',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2018-01-20T19:00:00')]
        )
        events_from_db = dao_get_future_events()

        assert Event.query.count() == 2
        assert len(events_from_db) == 1
        assert events_from_db[0] == event

    @freeze_time("2018-01-10T19:00:00")
    def it_gets_past_year_events(self, db, db_session, sample_event_with_dates, sample_event_type):
        create_event(
            title='way past last year event',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2016-01-01T19:00:00')]
        )
        create_event(
            title='future event',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2018-01-20T19:00:00')]
        )
        events_from_db = dao_get_past_year_events()

        assert Event.query.count() == 3
        assert len(events_from_db) == 1
        assert events_from_db[0] == sample_event_with_dates

    def it_gets_events_in_year(self, db, db_session, sample_event_with_dates, sample_event_type):
        event_2 = create_event(
            title='2018 event',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2018-12-31T23:59:00')]
        )
        create_event(
            title='2017 event',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2017-12-31T23:59:59')]
        )
        create_event(
            title='2019 event',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2019-01-01T00:00:01')]
        )
        events_from_db = dao_get_events_in_year(2018)

        assert len(events_from_db) == 2
        assert events_from_db[0] == sample_event_with_dates
        assert events_from_db[1] == event_2

    def it_gets_limited_events(self, db, db_session, sample_event_with_dates, sample_event_type):
        event_2 = create_event(
            title='2018 event',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2018-12-31T23:59:00')]
        )
        create_event(
            title='beyond limit',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2017-12-31T23:59:59')]
        )
        events_from_db = dao_get_limited_events(2)

        assert len(events_from_db) == 2
        assert events_from_db[0] == event_2
        assert events_from_db[1] == sample_event_with_dates
