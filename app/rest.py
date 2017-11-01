from flask import Blueprint, Flask, jsonify, request, current_app

from app import db
from app.errors import register_errors

base_blueprint = Blueprint('', __name__, url_prefix='/')
register_errors(base_blueprint)


@base_blueprint.route('')
def get_info():
    current_app.logger.info('get_info')
    query = 'SELECT version_num FROM alembic_version'
    full_name = db.session.execute(query).fetchone()[0]
    return jsonify(environment=current_app.config['ENVIRONMENT'], info=full_name)
