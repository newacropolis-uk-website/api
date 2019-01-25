import pytest
from flask import json, url_for
from tests.conftest import create_authorization_header
from app.models import User
from tests.db import create_user


class WhenGettingUsers(object):

    def it_returns_all_users(self, client, sample_user, db_session):
        response = client.get(
            url_for('users.get_users'),
            headers=[create_authorization_header()]
        )
        assert response.status_code == 200

        data = json.loads(response.get_data(as_text=True))

        assert len(data) == 1


class WhenGettingUserByID(object):

    def it_returns_correct_user(self, client, sample_user, db_session):
        response = client.get(
            url_for('user.get_user_by_email', email=str(sample_user.email)),
            headers=[create_authorization_header()]
        )
        assert response.status_code == 200

        json_resp = json.loads(response.get_data(as_text=True))
        assert json_resp['id'] == str(sample_user.id)


class WhenPostingUser(object):

    @pytest.mark.parametrize('data', [
        {'email': 'sarah@example.com', 'name': 'Sarah Black', 'access_area': ',email,'},
        {'email': 'diane@example.com', 'access_area': ',email,'}
    ])
    def it_creates_a_user_on_valid_post_data(self, client, data, db_session):
        response = client.post(
            url_for('user.create_user'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert response.status_code == 201

        json_resp = json.loads(response.get_data(as_text=True))
        for key in data.keys():
            assert data[key] == json_resp[key]

    @pytest.mark.parametrize('data,error_msg', [
        ({'email': 'bob@example.com'}, ['access_area is a required property']),
        ({'name': 'Sophia Grey', 'access_area': ',email,'}, ['email is a required property']),
        ({'name': 'Sophia Grey'}, ['email is a required property', 'access_area is a required property']),
    ])
    def it_returns_400_on_invalid_post_user_data(self, client, data, error_msg, db_session):
        response = client.post(
            url_for('user.create_user'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert response.status_code == 400

        json_resp = json.loads(response.get_data(as_text=True))
        assert all([e['error'] == "ValidationError" for e in json_resp['errors']])
        for i, err in enumerate(json_resp['errors']):
            assert json_resp['errors'][i]['message'] == error_msg[i]

    def it_updates_a_user_on_valid_post_data(self, client, sample_user, db_session):
        data = {'email': 'sarah@example.com', 'name': 'Sarah Black', 'access_area': ',email,'}
        response = client.post(
            url_for('user.update_user', user_id=str(sample_user.id)),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert response.status_code == 200

        json_resp = json.loads(response.get_data(as_text=True))
        for key in data.keys():
            assert data[key] == json_resp[key]

    def it_doesnt_create_user_with_same_email(self, client, db_session, sample_user):
        data = {'email': sample_user.email, 'name': 'Test user', 'access_area': ',email,'}

        response = client.post(
            url_for('user.create_user'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert response.status_code == 400

        json_resp = json.loads(response.get_data(as_text=True))
        assert json_resp['result'] == 'error'
        assert json_resp['message'] == 'User email already exists'

        users = User.query.all()
        assert len(users) == 1

    def it_returns_500_on_user_unknown_error(self, client, db_session):
        from app.routes.users.rest import handle_integrity_error

        class MockIntegrityError:
            def __str__(self):
                return 'other_key error'

        response, status = handle_integrity_error(MockIntegrityError())

        json_resp = json.loads(response.get_data(as_text=True))

        assert status == 500
        assert json_resp['message'] == 'Internal server error'
