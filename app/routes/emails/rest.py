from datetime import datetime, timedelta
import os
from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request
)

from flask_jwt_extended import jwt_required
from HTMLParser import HTMLParser

from app.comms.email import send_email
from app.dao.emails_dao import (
    dao_create_email,
    dao_get_email_by_id,
    dao_get_emails_for_year_starting_on,
    dao_update_email,
)

from app.dao.users_dao import dao_get_admin_users
from app.dao.events_dao import dao_get_event_by_old_id, dao_get_event_by_id

from app.routes.emails import get_nice_event_dates
from app.errors import register_errors, InvalidRequest

from app.models import Email, ANNOUNCEMENT, EVENT, MAGAZINE, MANAGED_EMAIL_TYPES
from app.routes.emails.schemas import (
    post_create_email_schema, post_update_email_schema, post_import_emails_schema, post_preview_email_schema
)
from app.schema_validation import validate

emails_blueprint = Blueprint('emails', __name__)
register_errors(emails_blueprint)
h = HTMLParser()


def get_email_html(data):
    if data['email_type'] == EVENT:
        event = dao_get_event_by_id(data.get('event_id'))
        return render_template(
            'emails/events.html',
            event=event,
            event_dates=get_nice_event_dates(event.event_dates),
            description=h.unescape(event.description),
            details=data.get('details', ''),
            extra_txt=data.get('extra_txt', ''),
        )


@emails_blueprint.route('/email/preview', methods=['POST'])
@jwt_required
def email_preview():
    data = request.get_json(force=True)

    validate(data, post_preview_email_schema)

    return get_email_html(data)


@emails_blueprint.route('/email', methods=['POST'])
@jwt_required
def create_email():
    data = request.get_json(force=True)

    validate(data, post_create_email_schema)

    subject = None
    if data['email_type'] == EVENT:
        event = dao_get_event_by_id(data.get('event_id'))
        subject = 'Please review {}'.format(event.title)

    email = Email(**data)

    dao_create_email(email)

    # send email to admin users and ask them to log in in order to approve the email
    for user in dao_get_admin_users():
        review_part = '<div>Please review this email: {}/emails/{}</div>'.format(
            current_app.config['FRONTEND_ADMIN_URL'], str(email.id))
        event_html = get_email_html(data)
        send_email(user.email, subject, review_part + event_html)

    return jsonify(email.serialize()), 201


@emails_blueprint.route('/email/types', methods=['GET'])
def get_email_types():
    return jsonify([{'type': email_type} for email_type in MANAGED_EMAIL_TYPES])


@emails_blueprint.route('/emails/import', methods=['POST'])
@jwt_required
def import_emails():
    data = request.get_json(force=True)

    validate(data, post_import_emails_schema)

    errors = []
    emails = []
    for item in data:
        err = ''
        email = Email.query.filter(Email.old_id == item['id']).first()
        if not email:
            event_id = None
            email_type = EVENT
            if int(item['eventid']) < 0:
                if item['eventdetails'].startswith('New Acropolis'):
                    email_type = MAGAZINE
                else:
                    email_type = ANNOUNCEMENT

            expires = None
            if email_type == EVENT:
                event = dao_get_event_by_old_id(item['eventid'])

                if not event:
                    err = u'event not found: {}'.format(item)
                    current_app.logger.info(err)
                    errors.append(err)
                    continue
                event_id = str(event.id)
                expires = event.get_last_event_date()
            else:
                # default to 2 weeks expiry after email was created
                expires = datetime.strptime(item['timestamp'], "%Y-%m-%d %H:%M") + timedelta(weeks=2)

            email = Email(
                event_id=event_id,
                old_id=item['id'],
                old_event_id=item['eventid'],
                details=item['eventdetails'],
                extra_txt=item['extratxt'],
                replace_all=True if item['replaceAll'] == 'y' else False,
                email_type=email_type,
                created_at=item['timestamp'],
                send_starts_at=item['timestamp'],
                expires=expires
            )

            dao_create_email(email)
            emails.append(email)
        else:
            err = u'email already exists: {}'.format(email.old_id)
            current_app.logger.info(err)
            errors.append(err)

    res = {
        "emails": [e.serialize() for e in emails]
    }

    if errors:
        res['errors'] = errors

    return jsonify(res), 201 if emails else 400 if errors else 200
