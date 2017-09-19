import os
from flask import (
    Blueprint,
    current_app,
    jsonify,
    request
)

from app import logging

from app.dao.fees_dao import dao_create_fee, dao_get_fees, dao_update_fee
from app.errors import register_errors

from app.fees.schemas import post_create_fee_schema
from app.models import Fee
from app.schema_validation import validate

fees_blueprint = Blueprint('fees', __name__, url_prefix='/fees')
register_errors(fees_blueprint)


@fees_blueprint.route('')
def get_fees():
    current_app.logger.info('get_fees')
    fees = [f.serialize() if f else None for f in dao_get_fees()]
    return jsonify(data=fees)


@fees_blueprint.route('', methods=['POST'])
def create_fee():
    data = request.get_json()

    validate(data, post_create_fee_schema)

    fee = Fee(**data)

    dao_create_fee(fee)
    return jsonify(data=fee.serialize()), 201
