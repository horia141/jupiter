"""Create metric entry history table

Revision ID: 646fd1d19041
Revises: 13c697b1b989
Create Date: 2021-02-25 17:24:11.067183

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '646fd1d19041'
down_revision = '13c697b1b989'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'metric_entry_event',
        sa.Column('owner_ref_id', sa.Integer, sa.ForeignKey('metric_entry.ref_id'), primary_key=True),
        sa.Column('timestamp', sa.DateTime, primary_key=True),
        sa.Column('session_index', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(32), primary_key=True),
        sa.Column('data', sa.JSON, nullable=True))


def downgrade() -> None:
    op.drop_table('metric_entry_history')
