import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Blueprint, Flask, jsonify, request
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
application = Flask(__name__)
jwt = JWTManager(application)


def create_app(**kwargs):
    from app.config import configs

    environment_state = get_env()

    application.config.from_object(configs[environment_state])
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    application.config['JWT_SECRET_KEY'] = 'super-secret'
    application.config['JWT_BLACKLIST_ENABLED'] = True
    application.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']

    # application.config['JWT_TOKEN_LOCATION'] = 'cookies'

    if kwargs:
        application.config.update(kwargs)

    configure_logging()

    db_name = application.config.get('SQLALCHEMY_DATABASE_URI').split('/')[-1]
    application.logger.debug("connected to db: {}".format(db_name))

    db.init_app(application)

    register_blueprint()

    return application


def register_blueprint():
    from app.rest import base_blueprint
    from app.events.rest import events_blueprint
    from app.fees.rest import fees_blueprint, fee_blueprint
    from app.event_types.rest import event_types_blueprint, event_type_blueprint
    from app.authentication.rest import auth_blueprint
    application.register_blueprint(base_blueprint)
    application.register_blueprint(auth_blueprint)
    application.register_blueprint(events_blueprint)
    application.register_blueprint(event_types_blueprint)
    application.register_blueprint(event_type_blueprint)
    application.register_blueprint(fees_blueprint)
    application.register_blueprint(fee_blueprint)


def get_env():
    if 'www-preview' in get_root_path():
        return 'preview'
    elif 'www-live' in get_root_path():
        return 'live'
    else:
        return os.environ.get('ENVIRONMENT', 'development')


def get_root_path():
    return application.root_path


def configure_logging():
    ch = logging.StreamHandler()
    if ch in application.logger.handlers:
        return

    del application.logger.handlers[:]

    f = GunicornTruncatingFormatter("%(asctime)s;[%(process)d];%(levelname)s;%(message)s", "%Y-%m-%d %H:%M:%S")

    if application.config['APP_SERVER'] == 'gunicorn':       
        gunicorn_access_logger = logging.getLogger('gunicorn.access')
        application.logger.handlers.extend(gunicorn_access_logger.handlers)

        gunicorn_error_logger = logging.getLogger('gunicorn.error')
        application.logger.handlers.extend(gunicorn_error_logger.handlers)

        rfh = RotatingFileHandler('logs/app.log', maxBytes=10000, backupCount=3)
        rfh.setLevel(logging.DEBUG)
        rfh.setFormatter(f)

        application.logger.addHandler(rfh)

        gunicorn_access_logger.addHandler(rfh)
        gunicorn_error_logger.addHandler(rfh)

        ch.setFormatter(f)

        gunicorn_access_logger.addHandler(ch)
        gunicorn_error_logger.addHandler(ch)

        application.logger.info('Gunicorn logging configured')
    else:
        ch.setFormatter(f)

        application.logger.addHandler(ch)

        werkzeug_log = logging.getLogger('werkzeug')
        werkzeug_log.setLevel(logging.DEBUG)

        rfh = RotatingFileHandler('logs/app.log', maxBytes=10000, backupCount=3)
        rfh.setLevel(logging.DEBUG)
        rfh.setFormatter(f)

        application.logger.addHandler(rfh)

        werkzeug_log.addHandler(rfh)

        application.logger.info('Flask logging configured')


class GunicornTruncatingFormatter(logging.Formatter):
    def format(self, record):
        GUNICORN_START_LOG = '127.0.0.1 - - ['
        if 'message' in dir(record) and record.msg[:15] == GUNICORN_START_LOG:
            record.msg = record.msg[42:]
        return super(GunicornTruncatingFormatter, self).format(record)
