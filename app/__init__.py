import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Blueprint, Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
application = Flask(__name__)


def create_app(**kwargs):
    from app.config import configs

    environment_state = get_env(application)

    application.config.from_object(configs[environment_state])
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    application.config['JWT_SECRET_KEY'] = 'super-secret'
    application.config.update(kwargs)

    jwt = JWTManager(application)

    configure_logging(application)

    application.logger.debug("connected to db: {}".format(application.config.get('SQLALCHEMY_DATABASE_URI')))

    db.init_app(application)

    register_blueprint(application)

    return application


def register_blueprint(application):
    from app.events.rest import events_blueprint
    from app.fees.rest import fees_blueprint, fee_blueprint
    from app.event_types.rest import event_types_blueprint, event_type_blueprint
    from app.authentication.rest import auth_blueprint
    application.register_blueprint(auth_blueprint)
    application.register_blueprint(events_blueprint)
    application.register_blueprint(event_types_blueprint)
    application.register_blueprint(event_type_blueprint)
    application.register_blueprint(fees_blueprint)
    application.register_blueprint(fee_blueprint)


def get_env(application):
    if 'www-preview' in get_root_path(application):
        return 'preview'
    elif 'www-live' in get_root_path(application):
        return 'live'
    else:
        return os.environ.get('ENVIRONMENT', 'development')


def get_root_path(application):
    return application.root_path


def configure_logging(application):
    del application.logger.handlers[:]

    f = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s", "%Y-%m-%d %H:%M:%S")

    rfh = RotatingFileHandler('logs/app.log', maxBytes=10000, backupCount=3)
    rfh.setLevel(logging.DEBUG)
    rfh.setFormatter(f)

    application.logger.addHandler(rfh)

    ch = logging.StreamHandler()
    ch.setFormatter(f)

    if ch not in application.logger.handlers:
        application.logger.addHandler(ch)

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.DEBUG)

    if rfh not in log.handlers:
        log.addHandler(rfh)

    if ch not in log.handlers:
        log.addHandler(ch)

    application.logger.info('Logging configured')
