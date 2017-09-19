import os
import logging

from flask import Blueprint, Flask
from flask_sqlalchemy import SQLAlchemy

logging.basicConfig(filename='logs/app.log', level=logging.DEBUG)
f = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s",
                              "%Y-%m-%d %H:%M:%S")
stream_log_handler = logging.StreamHandler()
stream_log_handler.setFormatter(f)
logging.getLogger().addHandler(stream_log_handler)

db = SQLAlchemy()
application = Flask(__name__)


def create_app(**kwargs):
    from app.config import configs

    environment_state = get_env()

    application.config.from_object(configs[environment_state])
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    application.config.update(kwargs)

    logging.debug("connected to db: {}".format(application.config.get('SQLALCHEMY_DATABASE_URI')))

    db.init_app(application)

    register_blueprint(application)

    return application


def register_blueprint(application):
    from app.events.rest import events_blueprint
    from app.fees.rest import fees_blueprint
    application.register_blueprint(events_blueprint)
    application.register_blueprint(fees_blueprint)


def get_env():
    if 'www-preview' in get_root_path():
        return 'preview'
    elif 'www-live' in get_root_path():
        return 'live'
    else:
        return os.environ.get('ENVIRONMENT', 'development')


def get_root_path():
    return application.root_path
