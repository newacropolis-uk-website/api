from app import db
from app.dao.decorators import transactional
from app.models import Marketing


@transactional
def dao_create_marketing(marketing):
    db.session.add(marketing)


@transactional
def dao_update_marketing(marketing_id, **kwargs):
    return Marketing.query.filter_by(id=marketing_id).update(
        kwargs
    )


def dao_get_marketing_by_id(marketing_id):
    return Marketing.query.filter_by(id=marketing_id).one()
