from datetime import datetime
from flask import (
    Blueprint,
    current_app,
    jsonify,
    request
)
import re

from flask_jwt_extended import jwt_required
from sqlalchemy.orm.exc import NoResultFound

from app.dao.events_dao import (
    dao_create_event,
    dao_delete_event,
    dao_get_events,
    dao_get_event_by_id,
    dao_get_events_in_year,
    dao_get_future_events,
    dao_get_limited_events,
    dao_get_past_year_events,
    dao_update_event,
)
from app.dao.event_dates_dao import dao_create_event_date, dao_get_event_date_by_id
from app.dao.event_types_dao import dao_get_event_type_by_old_id, dao_get_event_type_by_id
from app.dao.speakers_dao import dao_get_speaker_by_name, dao_get_speaker_by_id
from app.dao.venues_dao import dao_get_venue_by_old_id, dao_get_venue_by_id

from app.errors import register_errors, InvalidRequest
from app.models import Event, EventDate

from app.routes import is_running_locally
from app.routes.events.schemas import post_create_event_schema, post_import_events_schema

from app.schema_validation import validate

from app.storage.utils import Storage

events_blueprint = Blueprint('events', __name__)
register_errors(events_blueprint)


def extract_startdate(json):
    if json['event_dates']:
        return json['event_dates'][0]['event_datetime']
    else:
        return 0


@events_blueprint.route('/event', methods=['POST'])
@jwt_required
def create_event():
    data = request.get_json(force=True)
    event_year = None

    validate(data, post_create_event_schema)

    try:
        dao_get_event_type_by_id(data['event_type_id'])
    except NoResultFound:
        raise InvalidRequest('event type not found: {}'.format(data['event_type_id']), 400)

    try:
        dao_get_venue_by_id(data['venue_id'])
    except NoResultFound:
        raise InvalidRequest('venue not found: {}'.format(data['venue_id']), 400)

    event = Event(
        event_type_id=data['event_type_id'],
        title=data['title'],
        sub_title=data.get('sub_title'),
        description=data['description'],
        booking_code='',
        fee=data.get('fee'),
        conc_fee=data.get('conc_fee'),
        multi_day_fee=data.get('multi_day_fee'),
        multi_day_conc_fee=data.get('multi_day_conc_fee'),
        venue_id=data.get('venue_id')
    )

    for event_date in data.get('event_dates'):
        if not event_year:
            event_year = event_date['event_date'].split('-')[0]
        speakers = []
        for s in event_date.get('speakers', []):
            speaker = dao_get_speaker_by_id(s['speaker_id'])
            speakers.append(speaker)

        e = EventDate(
            event_datetime=event_date['event_date'],
            end_time=event_date.get('end_time'),
            speakers=speakers
        )

        dao_create_event_date(e)
        event.event_dates.append(e)

    dao_create_event(event)

    image_filename = data.get('image_filename')

    image_data = data.get('image_data')

    storage = Storage(current_app.config['STORAGE'])

    if image_data:
        target_image_filename = '{}/{}'.format(event_year, str(event.id))

        storage.upload_blob_from_base64string(image_filename, target_image_filename, image_data)

        image_filename = target_image_filename
    elif image_filename:
        if not storage.blob_exists(image_filename):
            raise InvalidRequest('{} does not exist'.format(image_filename), 400)

    event.image_filename = image_filename
    dao_update_event(event.id, image_filename=image_filename)

    return jsonify(event.serialize()), 201


@events_blueprint.route('/event/<uuid:event_id>', methods=['DELETE'])
@jwt_required
def delete_event(event_id):
    dao_delete_event(event_id)

    event = dao_get_event_by_id(event_id)
    if event:
        raise InvalidRequest("{} was not deleted".format(event_id), 500)
    current_app.logger.info('{} deleted'.format(event_id))
    return jsonify({'message': '{} deleted'.format(event_id)}), 200


@events_blueprint.route('/event/<uuid:event_id>', methods=['POST'])
@jwt_required
def update_event(event_id):
    data = request.get_json(force=True)

    validate(data, post_create_event_schema)

    try:
        event = dao_get_event_by_id(event_id)
    except NoResultFound:
        raise InvalidRequest('event not found: {}'.format(event_id), 400)

    try:
        dao_get_event_type_by_id(data['event_type_id'])
    except NoResultFound:
        raise InvalidRequest('event type not found: {}'.format(data['event_type_id']), 400)

    try:
        dao_get_venue_by_id(data['venue_id'])
    except NoResultFound:
        raise InvalidRequest('venue not found: {}'.format(data['venue_id']), 400)

    for event_date in data.get('event_dates'):
        speakers = []
        for s in event_date.get('speakers', []):
            speaker = dao_get_speaker_by_id(s['speaker_id'])
            speakers.append(speaker)

        event_date_id = event_date.get('event_date_id')
        if event_date_id:
            _event_date = dao_get_event_date_by_id(e['event_date_id'])
            _event_date.event_datetime = event_date['event_date']
            _event_date.speakers = speakers
        else:
            e = EventDate(
                event_datetime=event_date['event_date'],
                speakers=speakers
            )

            dao_create_event_date(e)
            event.event_dates.append(e)

    image_data = data.get('image_data')

    image_filename = data.get('image_filename')

    storage = Storage(current_app.config['STORAGE'])
    if image_data:
        storage.upload_blob_from_base64string(image_filename, image_filename, image_data)
    elif image_filename:
        if not storage.blob_exists(image_filename):
            raise InvalidRequest('{} does not exist'.format(image_filename), 400)

    dao_update_event(event_id, **data)

    return jsonify(event.serialize()), 200


@events_blueprint.route('/events')
@jwt_required
def get_events():
    events = [e.serialize() if e else None for e in dao_get_events()]

    events.sort(key=extract_startdate)
    return jsonify(events)


@events_blueprint.route('/events/year/<int:year>')
@jwt_required
def get_events_in_year(year):
    events = [e.serialize() if e else None for e in dao_get_events_in_year(year)]

    events.sort(key=extract_startdate)
    return jsonify(events)


@events_blueprint.route('/events/limit/<int:limit>')
@jwt_required
def get_limited_events(limit):
    if limit > current_app.config['EVENTS_MAX']:
        raise InvalidRequest("{} is greater than events max".format(limit), 400)

    events = [e.serialize() if e else None for e in dao_get_limited_events(limit)]

    return jsonify(events)


@events_blueprint.route('/events/future')
@jwt_required
def get_future_events():
    events = [e.serialize() if e else None for e in dao_get_future_events()]

    events.sort(key=extract_startdate)
    return jsonify(events)


@events_blueprint.route('/events/past_year')
@jwt_required
def get_past_year_events():
    events = [e.serialize() if e else None for e in dao_get_past_year_events()]

    events.sort(key=extract_startdate)
    return jsonify(events)


@events_blueprint.route('/events/extract-speakers', methods=['POST'])
def extract_speakers():
    data = request.get_json(force=True)
    validate(data, post_import_events_schema)

    speakers = []
    for item in data:
        speakers.append(item['Speaker'])

    sorted_speakers = [{"name": s} for s in sorted(set(speakers))]

    return jsonify(sorted_speakers), 200


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
            speakers = []

            event_type = dao_get_event_type_by_old_id(item['Type'])
            if not event_type:
                err = '{} event type not found: {}'.format(item['id'], item['Type'])
                current_app.logger.info(err)
                errors.append(err)

            if item['Speaker']:
                for s in re.split(r' and | & ', item['Speaker']):
                    speaker = dao_get_speaker_by_name(s)
                    if not speaker:
                        err = '{} speaker not found: {}'.format(item['id'], item['Speaker'])
                        current_app.logger.info(err)
                        errors.append(err)
                    else:
                        speakers.append(speaker)

            venue = dao_get_venue_by_old_id(item['venue'])
            if not venue:
                err = '{} venue not found: {}'.format(item['id'], item['venue'])
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
                fee=item['Fee'],
                conc_fee=item['ConcFee'],
                multi_day_fee=item['MultiDayFee'],
                multi_day_conc_fee=item['MultiDayConcFee'],
                duration=item['Duration'],
                venue_id=venue.id
            )

            def add_event_date(event_datetime):
                event_date = EventDate(
                    event_datetime=event_datetime,
                    duration=item['Duration'],
                    fee=item['Fee'],
                    conc_fee=item['ConcFee'],
                    multi_day_fee=item['MultiDayFee'],
                    multi_day_conc_fee=item['MultiDayConcFee'],
                    venue_id=venue.id
                )

                dao_create_event_date(event_date, speakers)

                event.event_dates.append(event_date)

            add_event_date(item['StartDate'])

            for i in range(2, 5):
                if item['StartDate{}'.format(i)] > '0000-00-00 00:00:00':
                    add_event_date(item['StartDate{}'.format(i)])

            events.append(event)
            dao_create_event(event)
        else:
            err = u'event already exists: {} - {}'.format(event.old_id, event.title)
            current_app.logger.info(err)
            errors.append(err)

        if is_running_locally() and item['ImageFilename'] and item['ImageFilename'] != '../spacer.gif':
            storage = Storage(current_app.config['STORAGE'])

            if not storage.blob_exists(item['ImageFilename']):
                storage.upload_blob("./data/events/{}".format(item['ImageFilename']), item['ImageFilename'])
            else:
                current_app.logger.info('{} found'.format(item['ImageFilename']))

    res = {
        "events": [e.serialize() for e in events]
    }

    if errors:
        res['errors'] = errors

    return jsonify(res), 201 if events else 400 if errors else 200
