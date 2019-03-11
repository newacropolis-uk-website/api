import copy
import pytest
from flask import json, url_for

from freezegun import freeze_time

from app.models import Event

from tests.conftest import create_authorization_header
from tests.db import create_event, create_event_date, create_event_type, create_speaker


@pytest.fixture
def sample_data(sample_speaker):
    create_event_type(old_id=2, event_type='excursion')

    data = [
        {
            "id": "1",
            "BookingCode": "",
            "MemberPay": "0",
            "Approved": "y",
            "Type": "1",
            "Title": "Philosophy of Economics",
            "SubTitle": "",
            "Description": "How Plato and Confucius can help understand economic development",
            "venue": "1",
            "Speaker": sample_speaker.name,
            "MultiDayFee": "10",
            "MultiDayConcFee": "8",
            "StartDate": "2004-09-20 19:30:00",
            "StartDate2": "2004-09-21 19:30:00",
            "StartDate3": "2004-09-22 19:30:00",
            "StartDate4": "2004-09-23 19:30:00",
            "EndDate": "0000-00-00 00:00:00",
            "Duration": "0",
            "Fee": "4",
            "ConcFee": "2",
            "Pub-First-Number": "3",
            "Mem-SignOn-Number": "12",
            "ImageFilename": "2004/Economics.jpg",
            "WebLink": "",
            "LinkText": None,
            "MembersOnly": "n",
            "RegisterStartOnly": "0",
            "SoldOut": None
        },
        {
            "id": "2",
            "BookingCode": "",
            "MemberPay": "0",
            "Approved": "y",
            "Type": "2",
            "Title": "Study Philosophy",
            "SubTitle": "",
            "Description": "16-week course introducing the major systems of thoughts from the East and West",
            "venue": "1",
            "Speaker": sample_speaker.name,
            "MultiDayFee": None,
            "MultiDayConcFee": "0",
            "StartDate": "2004-09-29 19:30:00",
            "StartDate2": "0000-00-00 00:00:00",
            "StartDate3": "0000-00-00 00:00:00",
            "StartDate4": "0000-00-00 00:00:00",
            "EndDate": "0000-00-00 00:00:00",
            "Duration": "0",
            "Fee": "96",
            "ConcFee": "64",
            "Pub-First-Number": "1",
            "Mem-SignOn-Number": "0",
            "ImageFilename": "2004/WinterCourse.jpg",
            "WebLink": "",
            "LinkText": "",
            "MembersOnly": "n",
            "RegisterStartOnly": "0",
            "SoldOut": None
        },
    ]

    return data


class WhenGettingEvents:

    def it_returns_all_events(self, client, sample_event, db_session):
        response = client.get(
            url_for('events.get_events'),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        data = json.loads(response.get_data(as_text=True))
        assert len(data) == 1

    @freeze_time("2018-01-10T19:00:00")
    def it_returns_all_future_events(self, client, sample_event_with_dates, sample_event_type, db_session):
        event_1 = create_event(
            title='future event',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2018-01-20T19:00:00')]
        )
        event_2 = create_event(
            title='future event',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2018-01-25T19:00:00')]
        )

        response = client.get(
            url_for('events.get_future_events'),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        data = json.loads(response.get_data(as_text=True))
        assert Event.query.count() == 3
        assert len(data) == 2
        assert data[0]['id'] == str(event_1.id)
        assert data[1]['id'] == str(event_2.id)

    @freeze_time("2018-01-10T19:00:00")
    def it_returns_past_year_events(self, client, sample_event_with_dates, sample_event_type, db_session):
        create_event(
            title='future event',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2018-01-20T19:00:00')]
        )
        create_event(
            title='way past year event',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2016-01-25T19:00:00')]
        )

        response = client.get(
            url_for('events.get_past_year_events'),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        data = json.loads(response.get_data(as_text=True))
        assert Event.query.count() == 3
        assert len(data) == 1
        assert data[0]['id'] == str(sample_event_with_dates.id)

    def it_returns_events_in_year(self, client, sample_event_with_dates, sample_event_type, db_session):
        event_2 = create_event(
            title='2018 event',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2018-01-20T19:00:00')]
        )
        create_event(
            title='way past year event',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2016-01-25T19:00:00')]
        )

        response = client.get(
            url_for('events.get_events_in_year', year=2018),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        data = json.loads(response.get_data(as_text=True))
        assert Event.query.count() == 3
        assert len(data) == 2
        assert data[0]['id'] == str(sample_event_with_dates.id)
        assert data[1]['id'] == str(event_2.id)

    def it_returns_limited_events(self, client, sample_event_with_dates, sample_event_type, db_session):
        event_2 = create_event(
            title='2018 event',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2018-01-20T19:00:00')]
        )
        create_event(
            title='beyond limit',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2016-01-25T19:00:00')]
        )

        response = client.get(
            url_for('events.get_limited_events', limit=2),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        data = json.loads(response.get_data(as_text=True))

        assert Event.query.count() == 3
        assert len(data) == 2
        assert data[0]['id'] == str(event_2.id)
        assert data[1]['id'] == str(sample_event_with_dates.id)

    def it_raises_400_returns_limited_events_more_than_events_max(
        self, client, sample_event_with_dates, sample_event_type, db_session
    ):
        create_event(
            title='2018 event',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2018-01-20T19:00:00')]
        )
        create_event(
            title='beyond limit',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2016-01-25T19:00:00')]
        )

        response = client.get(
            url_for('events.get_limited_events', limit=3),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 400

        data = json.loads(response.get_data(as_text=True))

        assert Event.query.count() == 3
        assert len(data) == 2
        assert data['message'] == '3 is greater than events max'

    def it_returns_all_events_with_event_dates(self, client, sample_speaker, sample_event_type, db_session):
        event_date_1 = create_event_date(event_datetime="2018-01-03")
        event_date_earliest = create_event_date(event_datetime="2018-01-01")
        event_date_2 = create_event_date(event_datetime="2018-01-02")

        create_event(event_type_id=sample_event_type.id, event_dates=[event_date_1, event_date_2])
        create_event(event_type_id=sample_event_type.id, event_dates=[event_date_2])
        create_event(event_type_id=sample_event_type.id, event_dates=[event_date_earliest])

        response = client.get(
            url_for('events.get_events'),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        data = json.loads(response.get_data(as_text=True))
        assert len(data) == 3
        assert data[0]['event_dates'][0]['event_datetime'] == str(event_date_earliest.event_datetime)[0:-3]


class WhenPostingExtractSpeakers:

    def it_extracts_unique_speakers_from_events_json(self, client, db_session, sample_data):
        event = copy.deepcopy(sample_data[0])
        event['Speaker'] = 'Gary Blue'
        sample_data.append(event)

        response = client.post(
            url_for('events.extract_speakers'),
            data=json.dumps(sample_data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert response.status_code == 200

        json_resp = json.loads(response.get_data(as_text=True))
        data_speakers = set([d['Speaker'] for d in sample_data])

        assert len(json_resp) == len(data_speakers)
        assert set([s['name'] for s in json_resp]) == data_speakers


class WhenPostingImportEvents(object):

    @pytest.fixture
    def mock_config(self, mocker):
        mocker.patch.dict('app.application.config', {
            'STORAGE': 'test-store'
        })

    @pytest.fixture
    def mock_storage(self, mocker):
        mock_storage = mocker.patch("app.storage.utils.Storage.__init__", return_value=None)
        mock_storage_blob_exists = mocker.patch("app.storage.utils.Storage.blob_exists")
        yield
        mock_storage.assert_called_with('test-store')
        mock_storage_blob_exists.assert_called_with('2004/WinterCourse.jpg')

    @pytest.fixture
    def mock_storage_not_exists(self, mocker):
        mock_storage = mocker.patch("app.storage.utils.Storage.__init__", return_value=None)
        mock_storage_blob_exists = mocker.patch("app.storage.utils.Storage.blob_exists", return_value=False)
        mock_storage_blob_upload = mocker.patch("app.storage.utils.Storage.upload_blob")
        yield
        mock_storage.assert_called_with('test-store')
        mock_storage_blob_exists.assert_called_with('2004/Economics.jpg')
        mock_storage_blob_upload.assert_called_with('./data/events/2004/Economics.jpg', '2004/Economics.jpg')

    def it_creates_events_for_imported_events(
        self, client, db_session, sample_event_type, sample_venue, sample_speaker, sample_data,
        mock_config, mock_storage
    ):
        response = client.post(
            url_for('events.import_events'),
            data=json.dumps(sample_data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert response.status_code == 201

        json_events = json.loads(response.get_data(as_text=True))['events']
        assert len(json_events) == len(sample_data)
        for i in range(0, len(sample_data) - 1):
            assert json_events[i]["old_id"] == int(sample_data[i]["id"])
            assert json_events[i]["title"] == sample_data[i]["Title"]
            assert json_events[i]["fee"] == int(sample_data[i]["Fee"])
            assert json_events[i]["conc_fee"] == int(sample_data[i]["ConcFee"])
            assert json_events[i]["multi_day_fee"] == int(sample_data[i]["MultiDayFee"])
            assert json_events[i]["multi_day_conc_fee"] == int(sample_data[i]["MultiDayConcFee"])
            assert json_events[i]["venue"]['name'] == sample_venue.name
            assert json_events[i]["venue"]['directions'] == sample_venue.directions

    def it_creates_multiple_speakers_for_imported_events_with_multiple_speakers(
        self, client, db_session, sample_event_type, sample_venue, sample_speaker, sample_data,
        mock_config, mock_storage
    ):
        speaker_1 = create_speaker(name='John Smith')
        sample_data[0]['Speaker'] = "{} and {}".format(sample_speaker.name, speaker_1.name)
        sample_data[1]['Speaker'] = sample_speaker.name + " & " + speaker_1.name
        response = client.post(
            url_for('events.import_events'),
            data=json.dumps(sample_data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert response.status_code == 201

        json_events = json.loads(response.get_data(as_text=True))['events']
        assert len(json_events) == len(sample_data)
        for i in range(0, len(sample_data) - 1):
            assert json_events[i]["old_id"] == int(sample_data[i]["id"])
            assert json_events[i]["title"] == sample_data[i]["Title"]
        assert json_events[0]["event_dates"][0]["speakers"] == [
            sample_speaker.serialize(), speaker_1.serialize()]
        assert len(json_events[0]["event_dates"]) == 4
        assert json_events[0]["event_dates"][0]['event_datetime'] == "2004-09-20 19:30"
        assert json_events[0]["event_dates"][1]['event_datetime'] == "2004-09-21 19:30"
        assert json_events[0]["event_dates"][2]['event_datetime'] == "2004-09-22 19:30"
        assert json_events[0]["event_dates"][3]['event_datetime'] == "2004-09-23 19:30"
        assert json_events[1]["event_dates"][0]["speakers"] == [
            sample_speaker.serialize(), speaker_1.serialize()]

    def it_ignores_existing_events_for_imported_events(
        self, client, db_session, sample_event_type, sample_venue, sample_speaker, sample_event, sample_data,
        mock_config, mock_storage
    ):
        response = client.post(
            url_for('events.import_events'),
            data=json.dumps(sample_data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert response.status_code == 201

        json_resp = json.loads(response.get_data(as_text=True))
        # should ignore the first data element but create the second one
        assert len(json_resp['events']) == len(sample_data) - 1
        assert json_resp['events'][0]['title'] == sample_data[1]['Title']
        assert str(json_resp['events'][0]['old_id']) == sample_data[1]['id']

    @pytest.mark.parametrize('field,desc', [
        ('Type', 'event type'),
        ('Speaker', 'speaker'),
        ('venue', 'venue')
    ])
    def it_adds_errors_to_list_for_a_non_existant_field(
        self, client, db_session, sample_event_type, sample_venue, sample_speaker, sample_data, field, desc,
        mock_config, mock_storage_not_exists
    ):
        sample_data[1][field] = "0"
        response = client.post(
            url_for('events.import_events'),
            data=json.dumps(sample_data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert response.status_code == 201

        json_resp = json.loads(response.get_data(as_text=True))
        assert len(json_resp['events']) == 1
        assert len(json_resp['errors']) == 1
        assert str(json_resp['events'][0]["old_id"]) == str(sample_data[0]["id"])
        assert json_resp['errors'][0] == "{} {} not found: 0".format(sample_data[1]["id"], desc)


@pytest.fixture
def sample_req_event_data(sample_event_type, sample_venue, sample_speaker):
    return {
        'event_type': sample_event_type,
        'venue': sample_venue,
        'speaker': sample_speaker
    }


class WhenCreatingAnEvent:

    def it_creates_an_event_via_rest(self, client, db_session, sample_req_event_data):
        data = {
            "event_type_id": sample_req_event_data['event_type'].id,
            "title": "Test title",
            "sub_title": "Test sub title",
            "description": "Test description",
            "image_filename": "test_img.png",
            "event_dates": [
                {
                    "event_date": "2019-03-01 19:00:00",
                    "speakers": [
                        {"speaker_id": sample_req_event_data['speaker'].id}
                    ]
                },
                {
                    "event_date": "2019-03-02 19:00:00",
                    "speakers": [
                        {"speaker_id": sample_req_event_data['speaker'].id}
                    ]
                }
            ],
            "venue_id": sample_req_event_data['venue'].id,
            "fee": 15,
            "conc_fee": 12,
        }

        response = client.post(
            url_for('events.create_event'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 201

        json_events = json.loads(response.get_data(as_text=True))
        assert json_events["title"] == data["title"]
        assert len(json_events["event_dates"]) == 2
        assert len(json_events["event_dates"][0]["speakers"]) == 1
        assert len(json_events["event_dates"][1]["speakers"]) == 1
        assert json_events["event_dates"][0]["speakers"][0]['id'] == sample_req_event_data['speaker'].serialize()['id']
        assert json_events["event_dates"][1]["speakers"][0]['id'] == sample_req_event_data['speaker'].serialize()['id']

    def it_creates_an_event_without_speakers_via_rest(self, client, db_session, sample_req_event_data):
        data = {
            "event_type_id": sample_req_event_data['event_type'].id,
            "title": "Test title",
            "sub_title": "Test sub title",
            "description": "Test description",
            "image_filename": "test_img.png",
            "event_dates": [
                {
                    "event_date": "2019-03-01 19:00:00",
                },
                {
                    "event_date": "2019-03-02 19:00:00",
                }
            ],
            "venue_id": sample_req_event_data['venue'].id,
            "fee": 15,
            "conc_fee": 12,
        }

        response = client.post(
            url_for('events.create_event'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 201

        json_events = json.loads(response.get_data(as_text=True))
        assert json_events["title"] == data["title"]
        assert len(json_events["event_dates"]) == 2
        assert len(json_events["event_dates"][0]["speakers"]) == 0
        assert len(json_events["event_dates"][1]["speakers"]) == 0

    def it_raises_400_when_missing_required_fields(self, client):
        response = client.post(
            url_for('events.create_event'),
            data='{}',
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 400

        data = json.loads(response.get_data(as_text=True))['errors']

        assert len(data) == 5
        assert data == [
            {"message": "event_type_id is a required property", "error": "ValidationError"},
            {"message": "title is a required property", "error": "ValidationError"},
            {"message": "description is a required property", "error": "ValidationError"},
            {"message": "event_dates is a required property", "error": "ValidationError"},
            {"message": "venue_id is a required property", "error": "ValidationError"}
        ]

    def it_raises_400_when_missing_event_date(self, client, db_session, sample_req_event_data):
        data = {
            "event_type_id": sample_req_event_data['event_type'].id,
            "title": "Test title",
            "sub_title": "Test sub title",
            "description": "Test description",
            "image_filename": "test_img.png",
            "event_dates": [],
            "venue_id": sample_req_event_data['venue'].id,
            "fee": 15,
            "conc_fee": 12,
        }
        response = client.post(
            url_for('events.create_event'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 400

        data = json.loads(response.get_data(as_text=True))['errors']

        assert len(data) == 1
        assert data == [
            {"message": "event_dates [] is too short", "error": "ValidationError"},
        ]
