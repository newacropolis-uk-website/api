import os
from flask import (
    Blueprint,
    jsonify,
    request
)

from app import logging

from app.dao.events_dao import dao_create_event, dao_get_events, dao_update_event

events_blueprint = Blueprint('events', __name__)


@events_blueprint.route('')
def get_events():
    logging.debug(os.environ.get("test_env"))
    events = [e.serialize() for e in dao_get_events()]
    return jsonify(data=events)
