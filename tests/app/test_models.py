from app.models import Event, Fee, Speaker
from tests.db import create_event, create_fee, create_speaker


class WhenUsingEventModel(object):

    def it_shows_event_info_id_on_str(self, db, db_session):
        event = create_event()

        assert str(event) == '<Event: id {}>'.format(event.id)


class WhenUsingFeeModel(object):

    def it_shows_fee_json_on_serialize(self, db, db_session):
        fee = create_fee(fee=5, conc_fee=3)

        assert fee.serialize() == {
            'id': str(fee.id),
            'event_type_id': str(fee.event_type_id),
            'fee': fee.fee,
            'conc_fee': fee.conc_fee,
            'multi_day_fee': fee.multi_day_fee,
            'multi_day_conc_fee': fee.multi_day_conc_fee,
            'valid_from': fee.valid_from.isoformat()
        }


class WhenUsingSpeakerModel(object):

    def it_shows_speaker_json_on_serialize(self, db, db_session):
        speaker = create_speaker()

        assert speaker.serialize() == {
            'id': str(speaker.id),
            'title': speaker.title,
            'name': speaker.name,
            'alternate_names': speaker.alternate_names
        }

    def it_gets_last_name_correctly(self, db, db_session):
        speaker = create_speaker(name='John Smith')

        assert speaker.last_name == 'Smith'
