"""Create metric history table


Revision ID: 13c697b1b989
Revises: 4328006234c6
Create Date: 2021-02-24 15:52:16.342543

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '13c697b1b989'
down_revision = '4328006234c6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'metric_event',
        sa.Column('owner_ref_id', sa.Integer, sa.ForeignKey('metric.ref_id'), primary_key=True),
        sa.Column('timestamp', sa.DateTime, primary_key=True),
        sa.Column('session_index', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(32), primary_key=True),
        sa.Column('data', sa.JSON, nullable=True))


def downgrade():
    op.drop_table('metric_history')
