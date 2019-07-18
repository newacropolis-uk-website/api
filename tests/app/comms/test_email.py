from mock import call
import pytest

from app.comms.email import send_email


@pytest.fixture
def mock_config(mocker):
    mocker.patch(
        'flask.current_app.config',
        {
            'DEBUG': True,
            'EMAIL_DOMAIN': 'example.com',
            'EMAIL_PROVIDER_URL': '',
            'EMAIL_PROVIDER_APIKEY': ''
        }
    )


class WhenSendingAnEmail:

    def it_logs_the_email_if_no_email_config(self, app, mocker, mock_config):
        mock_logger = mocker.patch('app.comms.email.current_app.logger.info')
        send_email('test@example.com', 'test subject', 'test message')

        assert mock_logger.call_args == call(
            "Email not configured, email would have sent: {'to': 'test@example.com', 'html': 'test message',"
            " 'from': 'noreply@example.com', 'subject': 'test subject'}")
