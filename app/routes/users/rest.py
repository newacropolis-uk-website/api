from flask import (
    Blueprint,
    current_app,
    jsonify,
    request
)
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from app.dao.users_dao import dao_get_users, dao_get_user_by_email, dao_get_user_by_id, dao_create_user, dao_update_user
from app.errors import register_errors
from app.models import User
from app.schema_validation import validate
from app.routes.users.schemas import (
    post_create_user_schema,
    # post_create_users_schema,
    # post_import_users_schema,
    post_update_user_schema
)

users_blueprint = Blueprint('users', __name__)
user_blueprint = Blueprint('user', __name__)

register_errors(users_blueprint)
register_errors(user_blueprint)


@users_blueprint.route('/users')
@jwt_required
def get_users():
    users = [s.serialize() if s else None for s in dao_get_users()]
    return jsonify(users)


@user_blueprint.route('/user/<email>', methods=['GET'])
@jwt_required
def get_user_by_email(email):
    user = dao_get_user_by_email(email)
    return jsonify(user.serialize())


@user_blueprint.route('/user', methods=['POST'])
@jwt_required
def create_user():
    data = request.get_json(force=True)

    validate(data, post_create_user_schema)

    user = User(**data)

    dao_create_user(user)
    return jsonify(user.serialize()), 201


@user_blueprint.route('/user/<uuid:user_id>', methods=['POST'])
@jwt_required
def update_user(user_id):
    data = request.get_json(force=True)

    validate(data, post_update_user_schema)

    dao_update_user(user_id, **data)

    user = dao_get_user_by_id(user_id)

    return jsonify(user.serialize()), 200


@user_blueprint.errorhandler(IntegrityError)
def handle_integrity_error(exc):
    """
    Handle integrity errors caused by the unique constraint on users_email_key
    """
    if 'users_email_key' in str(exc):
        return jsonify(result="error",
                       message="User email already exists"), 400

    current_app.logger.exception(exc)
    return jsonify(result='error', message="Internal server error"), 500
