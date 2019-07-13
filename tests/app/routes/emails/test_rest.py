import pytest

from flask import json, url_for

from app.models import ANNOUNCEMENT, EVENT, MAGAZINE, EMAIL_TYPES, Email
from tests.conftest import create_authorization_header, request, TEST_ADMIN_USER
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


class WhenGettingEmailTypes:
    def it_returns_email_types(self, client):
        response = client.get(
            url_for('emails.get_email_types'),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        json_email_types = json.loads(response.get_data(as_text=True))

        assert set(EMAIL_TYPES) == set([email_type['type'] for email_type in json_email_types])


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


class WhenPreviewingEmails:

    def it_returns_an_email_preview(self, client, db_session, sample_event_with_dates):
        data = {
            "event_id": str(sample_event_with_dates.id),
            "details": "<div>Some additional details</div>",
            "extra_txt": "<div>Some more information about the event</div>",
            "replace_all": False,
            "email_type": "event"
        }

        html = request(
            url_for('emails.email_preview'),
            client.post,
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()])

        assert html.soup.select_one('h3').text.strip() == 'Mon 1 of January - 7 PM'
        assert html.soup.select_one('.event_text h4').text == 'WORKSHOP: test_title'

        assert data['details'] in str(html.soup.select_one('.event_text'))
        assert data['extra_txt'] in str(html.soup.select_one('.event_text'))


class WhenPostingCreateEmail:

    def it_creates_an_event_email(self, mocker, client, db_session, sample_admin_user, sample_event_with_dates):
        mock_send_email = mocker.patch('app.routes.emails.rest.send_email')
        data = {
            "event_id": str(sample_event_with_dates.id),
            "details": "<div>Some additional details</div>",
            "extra_txt": "<div>Some more information about the event</div>",
            "replace_all": False,
            "email_type": "event"
        }

        response = client.post(
            url_for('emails.create_email'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        json_resp = json.loads(response.get_data(as_text=True))

        assert json_resp['email_type'] == 'event'
        assert not json_resp['old_id']
        assert json_resp['event_id'] == str(sample_event_with_dates.id)
        assert not json_resp['old_event_id']
        assert json_resp['extra_txt'] == '<div>Some more information about the event</div>'
        assert json_resp['details'] == '<div>Some additional details</div>'
        assert not json_resp['replace_all']

        emails = Email.query.all()

        assert len(emails) == 1
        assert emails[0].email_type == 'event'
        assert emails[0].event_id == sample_event_with_dates.id

        assert mock_send_email.call_args[0][0] == TEST_ADMIN_USER

    def it_does_not_create_an_event_email_if_no_event_matches(self, client, db_session, sample_uuid):
        data = {
            "event_id": sample_uuid,
            "details": "<div>Some additional details</div>",
            "extra_txt": "<div>Some more information about the event</div>",
            "replace_all": False,
            "email_type": "event"
        }

        response = client.post(
            url_for('emails.create_email'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 404

        json_resp = json.loads(response.get_data(as_text=True))

        assert json_resp['message'] == 'No result found'
        emails = Email.query.all()
        assert not emails
