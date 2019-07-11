from freezegun import freeze_time

from app.dao.emails_dao import dao_update_email, dao_get_emails_for_year_starting_on, dao_get_email_by_id
from app.models import Email, EVENT, MAGAZINE

from tests.db import create_email


class WhenUsingEmailsDAO(object):

    def it_creates_an_email(self, db_session):
        email = create_email()
        assert Email.query.count() == 1

        email_from_db = Email.query.filter(Email.id == email.id).first()

        assert email == email_from_db

    def it_updates_an_email_dao(self, db, db_session, sample_email):
        dao_update_email(sample_email.id, extra_txt='test update')

        email_from_db = Email.query.filter(Email.id == sample_email.id).first()

        assert email_from_db.extra_txt == 'test update'

    @freeze_time("2019-06-10T10:00:00")
    def it_gets_emails_from_starting_date_from_last_year(self, db, db_session, sample_email):
        emails = [create_email(details='more details', created_at='2019-01-01'), sample_email]

        emails_from_db = dao_get_emails_for_year_starting_on()
        assert Email.query.count() == 2
        assert set(emails) == set(emails_from_db)

    @freeze_time("2019-06-10T10:00:00")
    def it_gets_emails_from_starting_date_from_specified_date(self, db, db_session):
        emails = [
            create_email(details='more details', created_at='2019-02-01'),
            create_email(details='more details', created_at='2018-02-01')
        ]

        emails_from_db = dao_get_emails_for_year_starting_on('2018-01-01')
        assert len(emails_from_db) == 1
        assert emails[1] == emails_from_db[0]

    def it_gets_an_email_by_id(self, db, db_session, sample_email):
        email = create_email(details='new event details')

        fetched_email = dao_get_email_by_id(email.id)
        assert fetched_email == email
