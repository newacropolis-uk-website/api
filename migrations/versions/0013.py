"""empty message

Revision ID: 0013 add speaker id event dates
Revises: 0012 allow null speaker event
Create Date: 2018-09-21 01:04:47.027957

"""

# revision identifiers, used by Alembic.
revision = '0013 add speaker id event dates'
down_revision = '0012 allow null speaker event'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.add_column('event_dates', sa.Column('speaker_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(None, 'event_dates', 'speakers', ['speaker_id'], ['id'])
    op.drop_constraint(u'events_speaker_id_fkey', 'events', type_='foreignkey')
    op.drop_column('events', 'speaker_id')


def downgrade():
    op.add_column('events', sa.Column('speaker_id', postgresql.UUID(), autoincrement=False, nullable=True))
    op.create_foreign_key(u'events_speaker_id_fkey', 'events', 'speakers', ['speaker_id'], ['id'])
    op.drop_constraint(None, 'event_dates', type_='foreignkey')
    op.drop_column('event_dates', 'speaker_id')
