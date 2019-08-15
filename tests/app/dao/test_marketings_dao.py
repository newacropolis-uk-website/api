from sqlalchemy.exc import IntegrityError
import pytest

from app.dao.marketings_dao import (
    dao_update_marketing, dao_get_marketing_by_id, dao_get_marketings
)
from app.models import Marketing

from tests.db import create_marketing


class WhenUsingMarketingsDAO(object):

    def it_creates_an_marketing(self, db_session):
        marketing = create_marketing()
        assert Marketing.query.count() == 1

        marketing_from_db = Marketing.query.filter(Marketing.id == marketing.id).first()

        assert marketing == marketing_from_db

    def it_updates_a_marketing_dao(self, db, db_session, sample_marketing):
        dao_update_marketing(sample_marketing.id, description='New posters')

        marketing_from_db = Marketing.query.filter(Marketing.id == sample_marketing.id).first()

        assert marketing_from_db.description == 'New posters'

    def it_gets_all_active_marketings(self, db, db_session, sample_marketing):
        create_marketing(description='Email')
        create_marketing(description='Old magazine', active=False)

        fetched_marketings = dao_get_marketings()
        assert len(fetched_marketings) == 2

    def it_gets_an_marketing_by_id(self, db, db_session, sample_marketing):
        marketing = create_marketing(description='Email')

        fetched_marketing = dao_get_marketing_by_id(marketing.id)
        assert fetched_marketing == marketing

    def it_doesnt_create_marketings_with_same_description(self, db_session, sample_marketing):
        with pytest.raises(expected_exception=IntegrityError):
            create_marketing(description=sample_marketing.description)

        marketings = Marketing.query.all()
        assert len(marketings) == 1

    def it_doesnt_update_marketingss_with_same_description(self, db_session, sample_marketing):
        marketing = create_marketing(description='New posters')
        with pytest.raises(expected_exception=IntegrityError):
            dao_update_marketing(str(marketing.id), description=sample_marketing.description)

        found_marketing = Marketing.query.filter(Marketing.id == marketing.id).one()
        assert found_marketing.description == 'New posters'
