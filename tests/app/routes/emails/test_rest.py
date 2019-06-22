import pytest

from flask import json, url_for

from app.models import ANNOUNCEMENT, EVENT, MAGAZINE
from tests.conftest import create_authorization_header
from tests.db import create_email


@pytest.fixture
def sample_emails():
    return [
        {
            "id": "1",
            "eventid": "-1",
            "eventdetails": "New Acropolis Newsletter Issue 1",
            "extratxt": "<a href='http://www.example.org/download.php?<member>&id=1'><img title="
            "'Click to download Issue 1' src='http://www.example.org/images/NA_Newsletter_Issue_1.pdf'></a>",
            "replaceAll": "n",
            "timestamp": "2019-01-01 10:00:00",
            "Title": "",
            "ImageFilename": "",
            "Status": "new",
            "limit_sending": "0"
        },
        {
            "id": "2",
            "eventid": "1",
            "eventdetails": "",
            "extratxt": "",
            "replaceAll": "n",
            "timestamp": "2019-02-01 11:00:00",
        },
        {
            "id": "3",
            "eventid": "-2",
            "eventdetails": "Some announcement",
            "extratxt": "",
            "replaceAll": "n",
            "timestamp": "2019-03-01 11:00:00",
        }
    ]


class WhenPostingImportingEmails:
    def it_creates_emails_for_imported_emails(
        self, client, db_session, sample_emails, sample_event
    ):
        response = client.post(
            url_for('emails.import_emails'),
            data=json.dumps(sample_emails),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert response.status_code == 201

        json_emails = json.loads(response.get_data(as_text=True))['emails']
        email_types = [MAGAZINE, EVENT, ANNOUNCEMENT]
        assert len(json_emails) == len(sample_emails)
        for i in range(0, len(sample_emails)):
            if json_emails[i]['email_type'] == EVENT:
                assert json_emails[i]['event_id'] == str(sample_event.id)
            assert json_emails[i]['email_type'] == email_types[i]
            assert json_emails[i]['created_at'] == sample_emails[i]['timestamp']
            assert json_emails[i]['extra_txt'] == sample_emails[i]['extratxt']
            assert json_emails[i]['details'] == sample_emails[i]['eventdetails']
            assert str(json_emails[i]['old_id']) == sample_emails[i]['id']
            assert str(json_emails[i]['old_event_id']) == sample_emails[i]['eventid']
            assert json_emails[i]['replace_all'] == (True if sample_emails[i]['replaceAll'] == 'y' else False)

    def it_doesnt_create_email_for_imported_emails_already_imported(
        self, client, db_session, sample_emails, sample_event
    ):
        create_email()  # email with old_id=1
        response = client.post(
            url_for('emails.import_emails'),
            data=json.dumps(sample_emails),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert response.status_code == 201

        json_resp = json.loads(response.get_data(as_text=True))
        json_emails = json_resp['emails']
        email_types = [EVENT, ANNOUNCEMENT]
        assert len(json_emails) == len(sample_emails) - 1
        for i in range(0, len(sample_emails) - 1):
            assert json_emails[i]['email_type'] == email_types[i]
            assert json_emails[i]['created_at'] == sample_emails[i + 1]['timestamp']
            assert json_emails[i]['extra_txt'] == sample_emails[i + 1]['extratxt']
            assert json_emails[i]['details'] == sample_emails[i + 1]['eventdetails']
            assert str(json_emails[i]['old_id']) == sample_emails[i + 1]['id']
            assert str(json_emails[i]['old_event_id']) == sample_emails[i + 1]['eventid']
            assert json_emails[i]['replace_all'] == (True if sample_emails[i + 1]['replaceAll'] == 'y' else False)
        json_errors = json_resp['errors']
        assert json_errors == ['email already exists: 1']

    def it_doesnt_create_email_for_imported_event_email_without_event(
        self, client, db_session, sample_emails
    ):
        response = client.post(
            url_for('emails.import_emails'),
            data=json.dumps(sample_emails),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert response.status_code == 201

        json_resp = json.loads(response.get_data(as_text=True))
        json_emails = json_resp['emails']
        email_types = [MAGAZINE, ANNOUNCEMENT]
        assert len(json_emails) == len(sample_emails) - 1
        offset = 0
        for i in range(0, len(sample_emails) - 1):
            if i == 1:
                offset = 1  # skip event email as shouldnt be created
            assert json_emails[i]['email_type'] == email_types[i]
            assert json_emails[i]['created_at'] == sample_emails[i + offset]['timestamp']
            assert json_emails[i]['extra_txt'] == sample_emails[i + offset]['extratxt']
            assert json_emails[i]['details'] == sample_emails[i + offset]['eventdetails']
            assert str(json_emails[i]['old_id']) == sample_emails[i + offset]['id']
            assert str(json_emails[i]['old_event_id']) == sample_emails[i + offset]['eventid']
            assert json_emails[i]['replace_all'] == (True if sample_emails[i + offset]['replaceAll'] == 'y' else False)
        json_errors = json_resp['errors']
        assert json_errors == ['event not found: {}'.format(
            {k.decode('utf8'): v.decode('utf8') for k, v in sample_emails[1].items()})]
