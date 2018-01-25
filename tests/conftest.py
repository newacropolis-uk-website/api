import os
import subprocess
import datetime

from bs4 import BeautifulSoup
from flask import current_app

import pytest
from alembic.command import upgrade
from alembic.config import Config
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
import sqlalchemy
from flask_jwt_extended import create_access_token, create_refresh_token

from app import create_app, db as _db, get_env
from tests.db import create_event, create_event_type, create_fee, create_speaker

TEST_DATABASE_URI = "postgresql://localhost/na_api_" + get_env() + '_test'


@pytest.yield_fixture(scope='session')
def app():
    _app = create_app(**{
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': TEST_DATABASE_URI,
        'PREFERRED_URL_SCHEME': 'http',
        'ADMIN_CLIENT_ID': 'testadmin',
        'ADMIN_CLIENT_SECRET': 'testsecret',
        'TOKEN_EXPIRY': 1
    })

    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope='session')
def db(app):
    assert _db.engine.url.database.endswith('_test'), 'dont run tests against main db'

    create_test_db_if_does_not_exist(_db)

    Migrate(app, _db)
    Manager(_db, MigrateCommand)
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    ALEMBIC_CONFIG = os.path.join(BASE_DIR, 'migrations')
    config = Config(ALEMBIC_CONFIG + '/alembic.ini')
    config.set_main_option("script_location", ALEMBIC_CONFIG)

    with app.app_context():
        upgrade(config, 'head')

    yield _db

    _db.session.remove()
    _db.get_engine(app).dispose()


@pytest.fixture(scope='function')
def db_session(db):
    yield db

    db.session.remove()
    for tbl in reversed(db.metadata.sorted_tables):
        # if tbl.name not in ["fees"]:
        db.engine.execute(tbl.delete())
    db.session.commit()


@pytest.fixture(scope='function')
def sample_event(db):
    return create_event(title='test_title', description='test description')


@pytest.fixture(scope='function')
def sample_event_type(db):
    return create_event_type(event_type='short course')


@pytest.fixture(scope='function')
def sample_fee(db, sample_event_type):
    return create_fee(fee=5, conc_fee=3, event_type_id=sample_event_type.id)


@pytest.fixture(scope='function')
def sample_speaker(db):
    return create_speaker(name='Paul White')


# token set around 2017-12-10T23:10:00
@pytest.fixture(scope='function')
def sample_decoded_token():
    start, expiry = get_unixtime_start_and_expiry()

    return {
        'jti': 'test',
        'exp': expiry,
        'iat': start,
        'fresh': False,
        'type': 'access',
        'nbf': start,
        'identity': 'admin'
    }


def create_test_db_if_does_not_exist(db):
    try:
        conn = db.engine.connect()
        conn.close()

    except sqlalchemy.exc.OperationalError as e:
        if 'database "{}" does not exist'.format(TEST_DATABASE_URI.split('/')[-1:][0]) in e.message:
            db_url = sqlalchemy.engine.url.make_url(TEST_DATABASE_URI)
            dbname = db_url.database

            if db_url.drivername == 'postgresql':
                subprocess.call(['/usr/bin/env', 'createdb', dbname])
        else:
            raise


def request(url, method, data=None, headers=None):
    r = method(url, data=data, headers=headers)
    r.soup = BeautifulSoup(r.get_data(as_text=True), 'html.parser')
    return r


def create_authorization_header(client_id='testadmin'):
    expires = datetime.timedelta(minutes=1)

    token = create_access_token(identity=client_id, expires_delta=expires)
    return 'Authorization', 'Bearer {}'.format(token)


def create_refresh_header(client_id='testadmin'):
    token = create_refresh_token(identity=client_id)
    return 'Authorization', 'Bearer {}'.format(token)


def get_unixtime_start_and_expiry(year=2017, month=12, day=10, hour=23, minute=10):
    from time import mktime
    d = datetime.datetime(year, month, day, hour, minute, 0)
    unixtime = mktime(d.timetuple())

    added_time = 900
    unixtime_expiry = unixtime + added_time
    return unixtime, unixtime_expiry
