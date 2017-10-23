import pytest

from flask import json, url_for, Blueprint, Flask
from flask_jwt_extended import (
    JWTManager,
    create_refresh_token,
    jwt_required
)
from freezegun import freeze_time

from app.errors import register_errors, NoAuthorizationError
from tests.conftest import request, create_authorization_header, create_refresh_header
from tests.db import create_fee


class WhenDoingLogin(object):

    def it_returns_an_access_token(self, client):
        data = {
            'username': 'testadmin',
            'password': 'testpassword'
        }
        response = client.post(
            url_for('auth.login'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json')]
        )
        json_resp = json.loads(response.get_data(as_text=True))
        assert json_resp['access_token']

    def it_does_not_return_an_access_token_for_invalid_username(self, client):
        data = {
            'username': 'invalid',
            'password': 'testpassword'
        }
        response = client.post(
            url_for('auth.login'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json')]
        )
        assert response.status_code == 403

        json_resp = json.loads(response.get_data(as_text=True))
        assert json_resp['message'] == 'Bad username or password'

    def it_does_not_return_an_access_token_for_invalid_password(self, client):
        data = {
            'username': 'testadmin',
            'password': 'invalid'
        }
        response = client.post(
            url_for('auth.login'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json')]
        )
        assert response.status_code == 403

        json_resp = json.loads(response.get_data(as_text=True))
        assert json_resp['message'] == 'Bad username or password'

    @pytest.mark.parametrize('data,error_msg', [
        ({'username': 'testuser'}, 'password is a required property'),
        ({'password': 'testpass'}, 'username is a required property'),
    ])
    def it_returns_400_on_invalid_login_post_data(self, client, data, error_msg):
        response = client.post(
            url_for('auth.login'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json')]
        )
        assert response.status_code == 400

        json_resp = json.loads(response.get_data(as_text=True))
        assert all([e['error'] == "ValidationError" for e in json_resp['errors']])
        assert json_resp['errors'][0]['message'] == error_msg


class WhenDoingLogout(object):

    def it_logs_the_user_out_and_adds_token_to_blacklist(self, client, mocker):
        mock = mocker.patch("app.authentication.rest.add_blacklist")
        mocker.patch("app.authentication.rest.get_raw_jwt", return_value={'jti': 'test'})
        response = client.post(
            url_for('auth.logout'),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert response.status_code == 200

        json_resp = json.loads(response.get_data(as_text=True))
        assert json_resp['logout']
        mock.assert_called_with('test')


class WhenRefreshingToken(object):

    def it_returns_a_valid_access_token(self, client, mocker):
        response = client.post(
            url_for('auth.refresh'),
            headers=[('Content-Type', 'application/json'), create_refresh_header()]
        )
        assert response.status_code == 200

        json_resp = json.loads(response.get_data(as_text=True))
        assert json_resp['access_token']

    def it_400_on_invalid_refresh_token(self, client, mocker):
        response = client.post(
            url_for('auth.refresh'),
            headers=[
                ('Content-Type', 'application/json'),
                ('Authorization', 'invalid')
            ]
        )
        assert response.status_code == 400

        json_resp = json.loads(response.get_data(as_text=True))
        assert json_resp['message'] == 'Invalid header error'


class WhenAccessingAProtectedEndpoint(object):

    @pytest.fixture
    def auth_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['JWT_SECRET_KEY'] = 'super-secret'
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 1
        jwt = JWTManager(app)

        auth_blueprint = Blueprint('authenticated_endpoint', __name__)
        register_errors(auth_blueprint)

        @auth_blueprint.route('/protected')
        @jwt_required
        def protected():
            return 'protected', 200

        @auth_blueprint.route('/unprotected')
        def unprotected():
            return 'unprotected', 200

        app.register_blueprint(auth_blueprint)

        with app.test_request_context(), app.test_client() as client:
            yield client

    def it_show_page_on_unprotected_endpoint(self, auth_app):
        response = auth_app.get(
            path='/unprotected'
        )

        assert response.status_code == 200
        assert response.data == 'unprotected'

    def it_show_page_if_valid_auth_token_provided(self, auth_app):
        response = auth_app.get(
            path='/protected',
            headers=[create_authorization_header()]
        )

        assert response.status_code == 200
        assert response.data == 'protected'

    def it_raises_401_if_no_auth_token_provided(self, auth_app):
        response = auth_app.get(
            path='/protected'
        )

        assert response.status_code == 401
        json_resp = json.loads(response.get_data(as_text=True))
        assert json_resp['message'] == 'Unauthorized, authentication token must be provided'

    def it_raises_400_if_invalid_auth_token_provided(self, auth_app):
        response = auth_app.get(
            path='/protected',
            headers=[('Authorization', 'Bearer invalid')]
        )

        assert response.status_code == 400
        json_resp = json.loads(response.get_data(as_text=True))
        assert json_resp['message'] == 'Decode error on auth token'

    @freeze_time("2017-10-20T11:00:00")
    def it_raises_401_if_token_expires(self, auth_app):
        auth_header = create_authorization_header()
        with freeze_time('2017-10-20T13:00:00'):
            response = auth_app.get(
                path='/protected',
                headers=[auth_header]
            )

        assert response.status_code == 401
        json_resp = json.loads(response.get_data(as_text=True))
        assert json_resp['message'] == 'Signature expired'
