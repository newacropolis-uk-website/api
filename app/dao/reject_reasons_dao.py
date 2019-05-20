from app import db
from app.dao.decorators import transactional
from app.models import RejectReason


@transactional
def dao_create_reject_reason(reject_reason):
    db.session.add(reject_reason)


@transactional
def dao_update_reject_reason(reject_reason_id, **kwargs):
    return RejectReason.query.filter_by(id=reject_reason_id).update(
        kwargs
    )
