"""Create metric entry table

Revision ID: 4328006234c6
Revises: f7af1fb194c3
Create Date: 2021-02-24 00:43:33.686101

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4328006234c6'
down_revision = 'f7af1fb194c3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'metric_entry',
        sa.Column('ref_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('archived', sa.Boolean, nullable=False),
        sa.Column('created_time', sa.DateTime, nullable=False),
        sa.Column('last_modified_time', sa.DateTime, nullable=False),
        sa.Column('archived_time', sa.DateTime, nullable=True),
        sa.Column('metric_ref_id', sa.Integer, sa.ForeignKey('metric.ref_id'), index=True, nullable=False),
        sa.Column('collection_time', sa.DateTime, nullable=False),
        sa.Column('value', sa.Float, nullable=False),
        sa.Column('notes', sa.UnicodeText, nullable=True))


def downgrade() -> None:
    op.drop_table('metric_entry')
