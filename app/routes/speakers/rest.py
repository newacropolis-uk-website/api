import os
from flask import (
    Blueprint,
    current_app,
    jsonify,
    request
)
from flask_jwt_extended import jwt_required
from sqlalchemy import inspect

from app import logging

from app.dao.speakers_dao import dao_get_speakers, dao_get_speaker_by_id, dao_create_speaker, dao_update_speaker
from app.errors import register_errors
from app.models import Speaker
from app.schema_validation import validate
from app.routes.speakers.schemas import (
    post_create_speaker_schema,
    post_create_speakers_schema,
    post_update_speaker_schema
)

speakers_blueprint = Blueprint('speakers', __name__, url_prefix='/speakers')
speaker_blueprint = Blueprint('speaker', __name__, url_prefix='/speaker')

register_errors(speakers_blueprint)
register_errors(speaker_blueprint)


@speakers_blueprint.route('')
@jwt_required
def get_speakers():
    speakers = [s.serialize() if s else None for s in dao_get_speakers()]
    return jsonify(speakers)


@speakers_blueprint.route('', methods=['POST'])
@jwt_required
def create_speakers():
    data = request.get_json(force=True)

    validate(data, post_create_speakers_schema)

    speakers = []
    for item in data:
        speaker = Speaker.query.filter(Speaker.name == item['name']).first()
        if not speaker:
            speaker = Speaker(**item)
            speakers.append(speaker)
            dao_create_speaker(speaker)
        else:
            current_app.logger.info('speaker already exists: {}'.format(speaker.name))
    return jsonify([s.serialize() for s in speakers]), 201


@speaker_blueprint.route('/<uuid:speaker_id>', methods=['GET'])
@jwt_required
def get_speaker_by_id(speaker_id):
    current_app.logger.info('get_speaker: {}'.format(speaker_id))
    speaker = dao_get_speaker_by_id(speaker_id)
    return jsonify(speaker.serialize())


@speaker_blueprint.route('', methods=['POST'])
@jwt_required
def create_speaker():
    data = request.get_json()

    validate(data, post_create_speaker_schema)

    speaker = Speaker(**data)

    dao_create_speaker(speaker)
    return jsonify(speaker.serialize()), 201


@speaker_blueprint.route('/<uuid:speaker_id>', methods=['POST'])
@jwt_required
def update_speaker(speaker_id):
    data = request.get_json()

    validate(data, post_update_speaker_schema)

    fetched_speaker = dao_get_speaker_by_id(speaker_id)

    dao_update_speaker(fetched_speaker, **data)

    return jsonify(fetched_speaker.serialize()), 200
