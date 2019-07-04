import os
from datetime import datetime
from flask import (
    abort,
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request
)

from flask_jwt_extended import jwt_required

from app.dao.emails_dao import (
    dao_create_email,
    dao_get_email_by_id,
    dao_get_emails_for_year_starting_on,
    dao_update_email,
)

from app.dao.events_dao import dao_get_event_by_old_id, dao_get_event_by_id

from app.routes.emails import get_nice_event_dates
from app.errors import register_errors, InvalidRequest

from app.models import Email, ANNOUNCEMENT, EVENT, MAGAZINE
from app.routes.emails.schemas import (
    post_create_email_schema, post_update_email_schema, post_import_emails_schema, post_preview_email_schema
)
from app.schema_validation import validate

emails_blueprint = Blueprint('emails', __name__)
register_errors(emails_blueprint)


@emails_blueprint.route('/preview/email', methods=['POST'])
@jwt_required
def preview_email():
    data = request.get_json(force=True)

    validate(data, post_preview_email_schema)

    if data['email_type'] == 'event':
        event = dao_get_event_by_id(data.get('event_id'))

        from HTMLParser import HTMLParser
        h = HTMLParser()

        images_url = os.getenv('IMAGES_URL', current_app.config['API_BASE_URL'] + '/images/')

        return render_template(
            'emails/events.html',
            event=event,
            event_dates=get_nice_event_dates(event.event_dates),
            description=h.unescape(event.description),
            details=data.get('details', ''),
            extra_txt=data.get('extra_txt', ''),
            api_base_url=current_app.config['API_BASE_URL'],
            frontend_url=current_app.config['FRONTEND_URL'],
            images_url=images_url
        )


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

            if email_type == EVENT:
                event = dao_get_event_by_old_id(item['eventid'])

                if not event:
                    err = u'event not found: {}'.format(item)
                    current_app.logger.info(err)
                    errors.append(err)
                    continue
                event_id = str(event.id)

            email = Email(
                event_id=event_id,
                old_id=item['id'],
                old_event_id=item['eventid'],
                details=item['eventdetails'],
                extra_txt=item['extratxt'],
                replace_all=True if item['replaceAll'] == 'y' else False,
                email_type=email_type,
                created_at=item['timestamp']
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
