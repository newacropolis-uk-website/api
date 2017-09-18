from app.dao.event_types_dao import dao_create_event_type, dao_update_event_type, dao_get_event_types
from app.models import EventType

from tests.db import create_event_type


class WhenUsingEventTypessDAO(object):

    def it_creates_an_event_type(self, db, db_session):
        event_type = create_event_type()

        assert EventType.query.count() == 1
        event_type_from_db = EventType.query.first()
        assert event_type == event_type_from_db

    def it_updates_an_event_type(self, db, db_session, sample_event_type):
        event_type = create_event_type(event_type='talk')
        dao_update_event_type(event_type, event_type='workshop')

        event_from_db = EventType.query.filter(EventType.id == event_type.id).first()

        assert event_type.event_type == 'workshop'

    def it_gets_all_event_types(self, db, db_session, sample_event_type):
        create_event_type(event_type='course')
        event_types = dao_get_event_types()

        assert EventType.query.count() == 2
        event_type_from_db = EventType.query.all()
        assert set(event_types) == set(event_type_from_db)
