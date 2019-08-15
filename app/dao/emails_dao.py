from datetime import datetime, timedelta
from sqlalchemy import and_

from app import db
from app.dao.decorators import transactional
from app.dao.members_dao import dao_get_member_by_id
from app.models import Email, EmailToMember


@transactional
def dao_create_email(email):
    db.session.add(email)


@transactional
def dao_update_email(email_id, **kwargs):
    if 'members_sent_to' in kwargs.keys():
        members_sent_to = kwargs.pop('members_sent_to')
    else:
        members_sent_to = None

    email_query = Email.query.filter_by(id=email_id)

    res = email_query.update(kwargs) if kwargs else None

    if members_sent_to is not None:
        email_query.one().members_sent_to = members_sent_to

    return res


@transactional
def dao_add_member_sent_to_email(email_id, member_id, status_code=200, created_at=None):
    if not created_at:
        created_at = datetime.strftime(datetime.now(), "%Y-%m-%d")

    email = dao_get_email_by_id(email_id)
    member = dao_get_member_by_id(member_id)

    if email.members_sent_to:
        email.members_sent_to.append(member)
    else:
        email.members_sent_to = [member]

    email_to_member = EmailToMember.query.filter_by(email_id=email.id, member_id=member.id).first()
    email_to_member.created_at = created_at
    email_to_member.status_code = status_code


@transactional
def dao_create_email_to_member(email_to_member):
    db.session.add(email_to_member)


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
