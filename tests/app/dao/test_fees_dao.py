import json

from app.dao.fees_dao import dao_create_fee, dao_update_fee, dao_get_fees, dao_get_fee_by_id
from app.models import Fee

from tests.db import create_fee


class WhenUsingFeesDAO(object):

    def it_creates_a_fee(self, db_session):
        fee = create_fee()
        assert Fee.query.count() == 1

        fee_from_db = Fee.query.filter(Fee.id == fee.id).first()

        assert fee == fee_from_db

    def it_updates_a_fee_dao(self, db, db_session, sample_fee):
        dao_update_fee(sample_fee.id, fee=10)

        fee_from_db = Fee.query.filter(Fee.id == sample_fee.id).first()

        assert sample_fee.fee == fee_from_db.fee

    def it_gets_all_fees(self, db, db_session, sample_fee):
        fees = [create_fee(fee=100, conc_fee=80), sample_fee]

        fees_from_db = dao_get_fees()
        assert Fee.query.count() == 2
        assert set(fees) == set(fees_from_db)

    def it_gets_a_fee_by_id(self, db, db_session, sample_fee):
        fee = create_fee(fee=100, conc_fee=80)

        fetched_fee = dao_get_fee_by_id(fee.id)
        assert fetched_fee == fee
