import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Blueprint, Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
application = Flask(__name__)


def create_app(**kwargs):
    from app.config import configs

    environment_state = get_env()

    application.config.from_object(configs[environment_state])
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    application.config.update(kwargs)

    configure_logging()

    application.logger.debug("connected to db: {}".format(application.config.get('SQLALCHEMY_DATABASE_URI')))

    db.init_app(application)

    register_blueprint()

    return application


def register_blueprint():
    from app.events.rest import events_blueprint
    from app.fees.rest import fees_blueprint
    from app.fees.rest import fee_blueprint
    application.register_blueprint(events_blueprint)
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
