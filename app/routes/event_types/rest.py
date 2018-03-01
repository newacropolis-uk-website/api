import os
from flask import (
    Blueprint,
    current_app,
    jsonify,
    request
)

from flask_jwt_extended import jwt_required

from app.dao.event_types_dao import (
    dao_create_event_type,
    dao_get_event_types,
    dao_update_event_type,
    dao_get_event_type_by_id
)
from app.errors import register_errors

from app.routes.event_types.schemas import post_create_event_type_schema, post_update_event_type_schema
from app.models import EventType
from app.schema_validation import validate

event_types_blueprint = Blueprint('event_types', __name__, url_prefix='/event_types')
event_type_blueprint = Blueprint('event_type', __name__, url_prefix='/event_type')
register_errors(event_types_blueprint)
register_errors(event_type_blueprint)


@event_types_blueprint.route('')
@jwt_required
def get_event_types():
    current_app.logger.info('get_event_types')
    event_types = [e.serialize() if e else None for e in dao_get_event_types()]
    return jsonify(data=event_types)


@event_type_blueprint.route('/<uuid:event_type_id>', methods=['GET'])
def get_event_type_by_id(event_type_id):
    current_app.logger.info('get_event_type: {}'.format(event_type_id))
    event_type = dao_get_event_type_by_id(event_type_id)
    return jsonify(data=event_type.serialize())


@event_type_blueprint.route('', methods=['POST'])
def create_event_type():
    data = request.get_json()

    validate(data, post_create_event_type_schema)

    event_type = EventType(**data)

    dao_create_event_type(event_type)
    return jsonify(data=event_type.serialize()), 201


@event_type_blueprint.route('/<uuid:event_type_id>', methods=['POST'])
def update_event_type(event_type_id):
    data = request.get_json()

    validate(data, post_update_event_type_schema)

    fetched_event_type = dao_get_event_type_by_id(event_type_id)

    dao_update_event_type(event_type_id, **data)

    return jsonify(data=fetched_event_type.serialize()), 200
