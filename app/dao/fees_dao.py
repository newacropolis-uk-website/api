from app import db
from app.dao.decorators import transactional
from app.models import Fee


@transactional
def dao_create_fee(fee):
    db.session.add(fee)


@transactional
def dao_update_fee(fee_obj, **kwargs):
    for key, value in kwargs.items():
        setattr(fee_obj, key, value)
    db.session.add(fee_obj)


def dao_get_fees():
    return Fee.query.order_by(Fee.event_type_id, Fee.valid_from.desc()).all()


def dao_get_fee_by_id(fee_id):
    return Fee.query.filter_by(id=fee_id).one()
