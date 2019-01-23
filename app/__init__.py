import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
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

    if kwargs:
        application.config.update(kwargs)

    configure_logging()

    db.init_app(application)

    register_blueprint()

    init_app(application)

    return application


def init_app(app):
    @app.before_request
    def check_for_apikey():
        # print("check: ", request)
        pass


def register_blueprint():
    from app.rest import base_blueprint
    from app.routes.articles.rest import article_blueprint, articles_blueprint
    from app.routes.authentication.rest import auth_blueprint
    from app.routes.events.rest import events_blueprint
    from app.routes.fees.rest import fees_blueprint, fee_blueprint
    from app.routes.event_dates.rest import event_dates_blueprint, event_date_blueprint
    from app.routes.event_types.rest import event_types_blueprint, event_type_blueprint
    from app.routes.speakers.rest import speakers_blueprint, speaker_blueprint
    from app.routes.users.rest import users_blueprint, user_blueprint
    from app.routes.venues.rest import venues_blueprint, venue_blueprint
    application.register_blueprint(base_blueprint)
    application.register_blueprint(auth_blueprint)
    application.register_blueprint(article_blueprint)
    application.register_blueprint(articles_blueprint)
    application.register_blueprint(events_blueprint)
    application.register_blueprint(event_date_blueprint)
    application.register_blueprint(event_dates_blueprint)
    application.register_blueprint(event_types_blueprint)
    application.register_blueprint(event_type_blueprint)
    application.register_blueprint(fees_blueprint)
    application.register_blueprint(fee_blueprint)
    application.register_blueprint(speakers_blueprint)
    application.register_blueprint(speaker_blueprint)
    application.register_blueprint(users_blueprint)
    application.register_blueprint(user_blueprint)
    application.register_blueprint(venues_blueprint)
    application.register_blueprint(venue_blueprint)


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
    if not application.config.get('APP_SERVER'):
        return

    ch = logging.StreamHandler()
    if ch in application.logger.handlers:
        return

    del application.logger.handlers[:]

    f = LogTruncatingFormatter("%(asctime)s;[%(process)d];%(levelname)s;%(message)s", "%Y-%m-%d %H:%M:%S")
    ch.setFormatter(f)
    application.logger.addHandler(ch)

    rfh = RotatingFileHandler('logs/app.log', maxBytes=10000, backupCount=3)
    rfh.setLevel(logging.DEBUG)
    rfh.setFormatter(f)

    application.logger.addHandler(rfh)

    if application.config.get('APP_SERVER') == 'gunicorn':
        gunicorn_access_logger = logging.getLogger('gunicorn.access')
        application.logger.handlers.extend(gunicorn_access_logger.handlers)

        gunicorn_error_logger = logging.getLogger('gunicorn.error')
        application.logger.handlers.extend(gunicorn_error_logger.handlers)

        gunicorn_access_logger.addHandler(rfh)
        gunicorn_error_logger.addHandler(rfh)

        gunicorn_access_logger.addHandler(ch)
        gunicorn_error_logger.addHandler(ch)

        application.logger.info('Gunicorn logging configured')
    else:
        werkzeug_log = logging.getLogger('werkzeug')
        werkzeug_log.setLevel(logging.DEBUG)

        werkzeug_log.addHandler(ch)
        werkzeug_log.addHandler(rfh)

        application.logger.info('Flask logging configured')

    db_name = application.config.get('SQLALCHEMY_DATABASE_URI').split('/')[-1]
    application.logger.debug("connected to db: {}".format(db_name))


class LogTruncatingFormatter(logging.Formatter):
    def format(self, record):
        START_LOG = '127.0.0.1 - - ['
        if 'msg' in dir(record) and record.msg[:15] == START_LOG:
            record.msg = record.msg[42:]
        return super(LogTruncatingFormatter, self).format(record)
