from app.models import Event, Fee
from tests.db import create_event, create_fee


class WhenUsingEventModel(object):

    def it_shows_event_info_id_on_str(self, db, db_session):
        event = create_event()

        assert str(event) == '<Event: id {}>'.format(event.id)


class WhenUsingFeeModel(object):

    def it_shows_json_obj_on_serialize(self, db, db_session):
        fee = create_fee(fee=5, conc_fee=3)

        assert fee.serialize() == {
            'id': str(fee.id),
            'event_type_id': str(fee.event_type_id),
            'fee': fee.fee,
            'conc_fee': fee.conc_fee,
            'multi_day_fee': fee.multi_day_fee,
            'multi_day_conc_fee': fee.multi_day_conc_fee,
            'created_at': fee.created_at.isoformat()
        }
