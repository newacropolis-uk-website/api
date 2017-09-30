from app.dao.event_types_dao import (
    dao_create_event_type,
    dao_update_event_type,
    dao_get_event_types,
    dao_get_event_type_by_id
)
from app.models import EventType

from tests.db import create_event_type, create_fee


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

    def it_gets_all_event_types(self, db_session, sample_event_type):
        create_event_type(event_type='course')

        event_types = dao_get_event_types()
        event_types_json = [e.serialize() for e in event_types]

        assert EventType.query.count() == 2

        event_types_from_db = EventType.query.all()
        event_types_from_db_json = [e.serialize() for e in event_types_from_db]

        assert sorted([e.values() for e in event_types_json]) == \
            sorted([e.values() for e in event_types_from_db_json])

    def it_gets_an_event_type(self, db, db_session, sample_event_type):
        event_type = dao_get_event_type_by_id(str(sample_event_type.id))

        assert event_type.id == sample_event_type.id

    def it_gets_an_event_type_with_fees_ordered(self, db, db_session, sample_event_type):
        fees = [
            create_fee(event_type_id=str(sample_event_type.id), created_at='2017-01-01'),
            create_fee(event_type_id=str(sample_event_type.id), fee=8, conc_fee=6, created_at='2017-02-01'),
            create_fee(event_type_id=str(sample_event_type.id), fee=10, conc_fee=7)
        ]

        event_type = dao_get_event_type_by_id(str(sample_event_type.id))
        assert event_type.id == sample_event_type.id
        assert len(event_type.fees) == 3
        assert sorted(fees, key=lambda f: getattr(f, 'created_at'), reverse=True) == event_type.fees
