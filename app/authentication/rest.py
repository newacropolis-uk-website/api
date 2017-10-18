from flask import (
    Blueprint,
    current_app,
    jsonify,
    request
)
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
    get_jwt_identity,
    get_raw_jwt
)
from app import jwt
from app.authentication.schemas import post_login_schema
from app.errors import register_errors
from app.schema_validation import validate

blacklist = set()
auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')
register_errors(auth_blueprint)


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist


@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    validate(data, post_login_schema)

    username = data['username']
    password = data['password']

    if username != current_app.config['ADMIN_CLIENT_ID'] or password != current_app.config['ADMIN_PASSWORD']:
        return jsonify({"msg": "Bad username or password"}), 401

    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=username)
    resp = jsonify({'login': True, 'access_token': access_token})
    # TODO set_refresh_cookies(resp, refresh_token)
    return resp, 200


@auth_blueprint.route('/logout', methods=['POST'])
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"logout": True}), 200
