"""empty message

Revision ID: 0001 Add event_types,events,fees
Revises: None
Create Date: 2017-09-23 23:39:03.972735

"""

# revision identifiers, used by Alembic.
revision = '0001 Add event_types,events,fees'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table('event_types',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('old_id', sa.Integer(), nullable=True),
    sa.Column('event_type', sa.String(length=255), nullable=True, unique=True),
    sa.Column('event_desc', sa.String(), nullable=True),
    sa.Column('event_filename', sa.String(length=255), nullable=True),
    sa.Column('duration', sa.Integer(), nullable=True),
    sa.Column('repeat', sa.Integer(), nullable=True),
    sa.Column('repeat_interval', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('events',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('old_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('sub_title', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('booking_code', sa.String(length=20), nullable=True),
    sa.Column('image_filename', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('fees',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('fee', sa.Integer(), nullable=False),
    sa.Column('conc_fee', sa.Integer(), nullable=False),
    sa.Column('multi_day_fee', sa.Integer(), nullable=True),
    sa.Column('multi_day_conc_fee', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.Date(), nullable=False),
    sa.Column('event_type_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.ForeignKeyConstraint(['event_type_id'], ['event_types.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('fees')
    op.drop_table('events')
    op.drop_table('event_types')
