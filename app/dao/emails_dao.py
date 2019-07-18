from datetime import datetime, timedelta
from sqlalchemy import and_

from app import db
from app.dao.decorators import transactional
from app.models import Email


@transactional
def dao_create_email(email):
    db.session.add(email)


@transactional
def dao_update_email(email_id, **kwargs):
    return Email.query.filter_by(id=email_id).update(
        kwargs
    )


def dao_get_emails_for_year_starting_on(date_starting=None):
    if not date_starting:
        date_starting = (datetime.today() - timedelta(weeks=52)).strftime("%Y-%m-%d")
        date_ending = datetime.today().strftime("%Y-%m-%d")
    else:
        date_ending = (datetime.strptime(date_starting, "%Y-%m-%d") + timedelta(weeks=52)).strftime("%Y-%m-%d")

    return Email.query.filter(
        and_(
            Email.created_at >= date_starting,
            Email.created_at < date_ending
        )
    ).order_by(Email.created_at.desc()).all()


def dao_get_email_by_id(email_id):
    return Email.query.filter_by(id=email_id).one()


def dao_get_future_emails():
    today = datetime.today().strftime("%Y-%m-%d")
    return Email.query.filter(
        Email.expires >= today
    ).all()
