from datetime import datetime, timedelta
from flask import current_app

from app import celery
from app.comms.email import send_email, get_email_html
from app.dao.emails_dao import dao_get_email_by_id, dao_add_member_sent_to_email
from app.dao.members_dao import dao_get_members_not_sent_to
from app.dao.users_dao import dao_get_admin_users
from app.models import EVENT


@celery.task()
def send_emails(email_id):
    members_not_sent_to = dao_get_members_not_sent_to(email_id)

    current_app.logger.info('Task send_emails received %s, sending %d emails', email_id, len(members_not_sent_to))

    email = dao_get_email_by_id(email_id)

    for member_id, email_to in members_not_sent_to:
        subject = email.get_subject()
        message = None
        if email.email_type == EVENT:
            message = get_email_html(
                email.email_type, event_id=email.event_id, details=email.details, extra_txt=email.extra_txt)

        email_status_code = send_email(email_to, subject, message)
        dao_add_member_sent_to_email(email_id, member_id, status_code=email_status_code)
