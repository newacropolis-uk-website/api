from app import db
from app.dao.decorators import transactional
from app.models import Venue


@transactional
def dao_create_venue(venue):
    default = dao_get_default_venue()
    if not default:
        venue.default = True

    db.session.add(venue)


@transactional
def dao_update_venue(venue_id, **kwargs):
    if 'default' in kwargs and kwargs['default'] is True:
        _reset_default_venue(venue_id)

    return Venue.query.filter_by(id=venue_id).update(
        kwargs
    )


def _reset_default_venue(venue_id):
    Venue.query.update({Venue.default: False})
    db.session.commit()


def dao_get_venues():
    return Venue.query.order_by(Venue.name).all()


def dao_get_venue_by_id(venue_id):
    return Venue.query.filter_by(id=venue_id).one()


def dao_get_default_venue():
    return Venue.query.filter_by(default=True).first()
