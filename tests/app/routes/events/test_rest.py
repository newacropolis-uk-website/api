import pytest
from flask import json, url_for
from tests.conftest import request


@pytest.fixture
def events_page(client):
    return request(url_for('events.get_events'), client.get)


class WhenGettingEvents(object):

    def it_returns_all_events(self, sample_event, events_page, db_session):
        data = json.loads(events_page.get_data(as_text=True))['data']
        assert len(data) == 1
