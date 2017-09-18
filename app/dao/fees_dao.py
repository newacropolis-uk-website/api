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
    return Fee.query.order_by(Fee.id).all()
