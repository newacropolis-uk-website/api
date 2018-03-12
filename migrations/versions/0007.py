"""empty message

Revision ID: 0007 add event_dates
Revises: 0006 add alternate_names speaker
Create Date: 2018-03-12 22:34:17.341718

"""

# revision identifiers, used by Alembic.
revision = '0007 add event_dates'
down_revision = '0006 add alternate_names speaker'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table('event_dates',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('event_datetime', sa.DateTime(), nullable=True),
    sa.Column('duration', sa.Integer(), nullable=True),
    sa.Column('soldout', sa.Boolean(), nullable=True),
    sa.Column('repeat', sa.Integer(), nullable=True),
    sa.Column('repeat_interval', sa.Integer(), nullable=True),
    sa.Column('fee', sa.Integer(), nullable=True),
    sa.Column('conc_fee', sa.Integer(), nullable=True),
    sa.Column('multi_day_fee', sa.Integer(), nullable=True),
    sa.Column('multi_day_conc_fee', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('event_dates')
