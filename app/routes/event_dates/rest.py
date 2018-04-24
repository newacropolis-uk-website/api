import os
from flask import (
    abort,
    Blueprint,
    current_app,
    jsonify,
    request
)

from flask_jwt_extended import jwt_required

from app.dao.event_dates_dao import (
    dao_create_event_date,
    dao_get_event_dates,
    dao_update_event_date,
    dao_get_event_date_by_id,
    dao_has_event_id_and_datetime
)
from app.errors import register_errors, InvalidRequest

from app.routes.event_dates.schemas import post_create_event_date_schema, post_update_event_date_schema
from app.models import EventDate
from app.schema_validation import validate

event_dates_blueprint = Blueprint('event_dates', __name__, url_prefix='/event_dates')
event_date_blueprint = Blueprint('event_date', __name__, url_prefix='/event_date')
register_errors(event_dates_blueprint)
register_errors(event_date_blueprint)


@event_dates_blueprint.route('')
@jwt_required
def get_event_dates():
    current_app.logger.info('get_event_dates')
    event_dates = [e.serialize() if e else None for e in dao_get_event_dates()]
    return jsonify(data=event_dates)


@event_date_blueprint.route('/<uuid:event_date_id>', methods=['GET'])
def get_event_date_by_id(event_date_id):
    current_app.logger.info('get_event_date: {}'.format(event_date_id))
    event_date = dao_get_event_date_by_id(event_date_id)
    return jsonify(data=event_date.serialize())


@event_date_blueprint.route('', methods=['POST'])
def create_event_date():
    data = request.get_json()

    validate(data, post_create_event_date_schema)

    check_event_id_and_datetime(data['event_id'], data['event_datetime'])

    event_date = EventDate(**data)

    dao_create_event_date(event_date)
    return jsonify(data=event_date.serialize()), 201


@event_date_blueprint.route('/<uuid:event_date_id>', methods=['POST'])
def update_event_date(event_date_id):
    data = request.get_json()

    validate(data, post_update_event_date_schema)

    fetched_event_date = dao_get_event_date_by_id(event_date_id)

    check_event_id_and_datetime(fetched_event_date.event_id, data['event_datetime'])

    dao_update_event_date(event_date_id, **data)

    return jsonify(data=fetched_event_date.serialize()), 200


def check_event_id_and_datetime(event_id, datetime):
    if dao_has_event_id_and_datetime(event_id, datetime):
        raise InvalidRequest("{} already exists for {}".format(datetime, event_id), 400)
