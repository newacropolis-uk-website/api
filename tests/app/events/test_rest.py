import pytest
from flask import json, url_for
from tests.conftest import request


@pytest.fixture
def events_page(client):
    return request(url_for('events.get_events'), client.get)


class WhenCallingEventEndpoint(object):

    def it_returns_all_events(self, sample_events, events_page, db_session):
        events = events_page
        print(events.get_data(as_text=True))
        data = json.loads(events.get_data(as_text=True))['data']
        assert len(data) == len(sample_events)
