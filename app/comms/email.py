from flask import current_app, jsonify
import requests


def send_email(to, subject, message, _from=None):
    if not _from:
        _from = 'noreply@{}'.format(current_app.config['EMAIL_DOMAIN'])

    email_provider_url = current_app.config['EMAIL_PROVIDER_URL']
    email_provider_apikey = current_app.config['EMAIL_PROVIDER_APIKEY']

    data = {
        "from": _from,
        "to": to,
        "subject": subject,
        "html": message
    }

    if email_provider_url and email_provider_apikey:
        response = requests.post(
            email_provider_url,
            auth=('api', email_provider_apikey),
            data=data,
        )

        response.raise_for_status()
        current_app.logger.info('Sent email: {}'.format(subject))
    else:
        current_app.logger.info('Email not configured, email would have sent: {}'.format(data))
