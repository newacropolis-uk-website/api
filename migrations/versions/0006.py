"""empty message

Revision ID: 0006 add alternate_names speaker
Revises: 0005 Add speakers table
Create Date: 2018-02-28 23:11:00.863456

"""

# revision identifiers, used by Alembic.
revision = '0006 add alternate_names speaker'
down_revision = '0005 Add speakers table'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('speakers', sa.Column('alternate_names', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('speakers', 'alternate_names')
