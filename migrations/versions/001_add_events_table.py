"""empty message

Revision ID: 001_add_events_table
Revises: None
Create Date: 2017-08-07 15:49:16.932388

"""

# revision identifiers, used by Alembic.
revision = '001_add_events_table'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('events')
