import pytest

from flask import json, url_for
from tests.conftest import request

from tests.db import create_fee


class WhenGettingEventTypes(object):

    def it_returns_all_event_types(self, client, sample_event_type, db_session):
        response = client.get(
            url_for('event_types.get_event_types', event_type_id=str(sample_event_type.id))
        )
        assert response.status_code == 200

        json_resp = json.loads(response.get_data(as_text=True))['data']
        assert len(json_resp) == 1
        assert json_resp[0]['id'] == str(sample_event_type.id)


class WhenGettingEventTypeByID(object):

    def it_returns_correct_event_type(self, client, sample_event_type, db_session):
        response = client.get(
            url_for('event_type.get_event_type_by_id', event_type_id=str(sample_event_type.id))
        )
        assert response.status_code == 200

        json_resp = json.loads(response.get_data(as_text=True))['data']
        assert json_resp['id'] == str(sample_event_type.id)

    def it_returns_correct_event_type_with_fees(self, client, sample_event_type, db_session):
        fees = [
            create_fee(event_type_id=str(sample_event_type.id)),
            create_fee(event_type_id=str(sample_event_type.id), fee=10, conc_fee=7)
        ]

        response = client.get(
            url_for('event_type.get_event_type_by_id', event_type_id=str(sample_event_type.id))
        )
        assert response.status_code == 200

        json_resp = json.loads(response.get_data(as_text=True))['data']
        assert json_resp['id'] == str(sample_event_type.id)

        for i, fee in enumerate(fees):
            assert json_resp['fees'][i]['fee'] == fee.fee
            assert json_resp['fees'][i]['conc_fee'] == fee.conc_fee


class WhenPostingEventType(object):

    @pytest.mark.parametrize('data', [
        {'event_type': 'Seminar'},
        {'event_type': 'Seminar', 'event_desc': 'Seminar test'},
    ])
    def it_creates_an_event_type_on_valid_post_data(self, client, data, db_session):
        response = client.post(
            url_for('event_type.create_event_type'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json')]
        )
        assert response.status_code == 201

        json_resp = json.loads(response.get_data(as_text=True))
        for key in data.keys():
            assert data[key] == json_resp['data'][key]

    @pytest.mark.parametrize('data,error_msg', [
        ({'event_desc': 'Seminar test'}, 'event_type is a required property'),
    ])
    def it_returns_400_on_invalid_event_type_post_data(self, client, data, error_msg, db_session):
        response = client.post(
            url_for('event_type.create_event_type'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json')]
        )
        assert response.status_code == 400

        json_resp = json.loads(response.get_data(as_text=True))
        assert all([e['error'] == "ValidationError" for e in json_resp['errors']])
        assert json_resp['errors'][0]['message'] == error_msg

    def it_updates_an_event_type_on_valid_post_data(self, client, sample_event_type, db_session):
        data = {'event_desc': 'updated desc', 'duration': 90}
        response = client.post(
            url_for('event_type.update_event_type', event_type_id=sample_event_type.id),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json')]
        )
        assert response.status_code == 200

        json_resp = json.loads(response.get_data(as_text=True))
        for key in data.keys():
            assert data[key] == json_resp['data'][key]
