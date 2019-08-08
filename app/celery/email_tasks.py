from datetime import datetime, timedelta
from flask import current_app

from app import celery
from app.comms.email import send_email, get_email_html
from app.dao.emails_dao import dao_get_email_by_id
from app.dao.users_dao import dao_get_admin_users
from app.models import EVENT


@celery.task()
def send_emails(email_id):
    current_app.logger.info('Task send_emails received %s', email_id)

    # use admin emails for now as members until member emails imported
    emails_to = [admin.email for admin in dao_get_admin_users()]

    for email_to in emails_to:
        result = send_email_to.apply_async((str(email_id), email_to))
        current_app.logger.info('Task: send_email_to: %r, %r', str(email_id), result)


@celery.task()
def send_email_to(email_id, email_to):
    current_app.logger.info('Task send_email_to received %s %s', email_id, email_to)

    email = dao_get_email_by_id(email_id)

    subject = email.get_subject()
    message = None
    if email.email_type == EVENT:
        message = get_email_html(
            email.email_type, event_id=email.event_id, details=email.details, extra_txt=email.extra_txt)

    send_email(email_to, subject, message)
