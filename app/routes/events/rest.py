import os
from flask import (
    Blueprint,
    current_app,
    jsonify,
    request
)

from flask_jwt_extended import jwt_required

from app.dao.events_dao import dao_create_event, dao_get_events, dao_update_event
from app.dao.event_dates_dao import dao_create_event_date
from app.dao.event_types_dao import dao_get_event_type_by_old_id
from app.dao.speakers_dao import dao_get_speaker_by_name
from app.dao.venues_dao import dao_get_venue_by_old_id

from app.errors import register_errors, InvalidRequest
from app.models import Event, EventDate

from app.schema_validation import validate

from app.routes.events.schemas import post_import_events_schema

events_blueprint = Blueprint('events', __name__)
register_errors(events_blueprint)


@events_blueprint.route('/events')
def get_events():
    events = [e.serialize() if e else None for e in dao_get_events()]
    return jsonify(events)


@events_blueprint.route('/events/extract-speakers', methods=['POST'])
def extract_speakers():
    data = request.get_json(force=True)
    validate(data, post_import_events_schema)

    speakers = []
    for item in data:
        speakers.append(item['Speaker'])

    return jsonify([{"name": s} for s in set(speakers)]), 200


@events_blueprint.route('/events/import', methods=['POST'])
@jwt_required
def import_events():
    data = request.get_json(force=True)

    validate(data, post_import_events_schema)

    errors = []
    events = []
    for item in data:
        err = ''
        event = Event.query.filter(Event.old_id == item['id']).first()
        if not event:

            event_type = dao_get_event_type_by_old_id(item['Type'])
            if not event_type:
                err = 'event type not found: {}'.format(item['Type'])
                current_app.logger.info(err)
                errors.append(err)

            if item['Speaker']:
                speaker = dao_get_speaker_by_name(item['Speaker'])
                if not speaker:
                    err = 'speaker not found: {}'.format(item['Speaker'])
                    current_app.logger.info(err)
                    errors.append(err)

            venue = dao_get_venue_by_old_id(item['venue'])
            if not venue:
                err = 'venue not found: {}'.format(item['venue'])
                current_app.logger.info(err)
                errors.append(err)

            if err:
                continue

            event = Event(
                old_id=item['id'],
                event_type_id=event_type.id,
                title=item['Title'],
                sub_title=item['SubTitle'],
                description=item['Description'],
                booking_code=item['BookingCode'],
                image_filename=item['ImageFilename'],
            )
            events.append(event)
            dao_create_event(event)

            event_date = EventDate(
                event_id=event.id,
                event_datetime=item['StartDate'],
                duration=item['Duration'],
                fee=item['Fee'],
                conc_fee=item['ConcFee'],
                multi_day_fee=item['MultiDayFee'],
                multi_day_conc_fee=item['MultiDayConcFee'],
                speaker_id=speaker.id,
                venue_id=venue.id
            )

            dao_create_event_date(event_date)
        else:
            err = 'event already exists: {} - {}'.format(event.old_id, event.title)
            current_app.logger.info(err)
            errors.append(err)

    res = {
        "events": [e.serialize() for e in events]
    }

    if errors:
        res['errors'] = errors

    return jsonify(res), 201 if events else 400 if errors else 200
