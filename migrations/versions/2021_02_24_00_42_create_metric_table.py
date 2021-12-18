"""Create metric table

Revision ID: f7af1fb194c3
Revises: 
Create Date: 2021-02-24 00:42:06.827058

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7af1fb194c3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'metric',
        sa.Column('ref_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('archived', sa.Boolean, nullable=False),
        sa.Column('created_time', sa.DateTime, nullable=False),
        sa.Column('last_modified_time', sa.DateTime, nullable=False),
        sa.Column('archived_time', sa.DateTime, nullable=True),
        sa.Column('the_key', sa.String(64), nullable=False, index=True, unique=True),
        sa.Column('name', sa.Unicode(), nullable=False),
        sa.Column('collection_period', sa.String(), nullable=True),
        sa.Column('metric_unit', sa.String(), nullable=True))


def downgrade():
    op.drop_table('metric')
