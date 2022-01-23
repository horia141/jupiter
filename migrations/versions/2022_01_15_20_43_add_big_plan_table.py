"""Add big plan table

Revision ID: 500745bf02b0
Revises: ebfe65b98854
Create Date: 2022-01-15 20:43:43.408413

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '500745bf02b0'
down_revision = 'ebfe65b98854'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'big_plan',
        sa.Column('ref_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('version', sa.Integer, nullable=False),
        sa.Column('archived', sa.Boolean, nullable=False),
        sa.Column('created_time', sa.DateTime, nullable=False),
        sa.Column('last_modified_time', sa.DateTime, nullable=False),
        sa.Column('archived_time', sa.DateTime, nullable=True),
        sa.Column('big_plan_collection_ref_id', sa.Integer, sa.ForeignKey("big_plan_collection.ref_id"), index=True, nullable=False),
        sa.Column('name', sa.Unicode(), nullable=False),
        sa.Column('status', sa.String(16), nullable=False),
        sa.Column('actionable_date', sa.DateTime, nullable=True),
        sa.Column('due_date', sa.DateTime, nullable=True),
        sa.Column('notion_link_uuid', sa.String(16), nullable=False),
        sa.Column('accepted_time', sa.DateTime, nullable=True),
        sa.Column('working_time', sa.DateTime, nullable=True),
        sa.Column('completed_time', sa.DateTime, nullable=True))
    op.create_table(
        'big_plan_event',
        sa.Column('owner_ref_id', sa.Integer, sa.ForeignKey('big_plan.ref_id'), primary_key=True),
        sa.Column('timestamp', sa.DateTime, primary_key=True),
        sa.Column('session_index', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(32), primary_key=True),
        sa.Column('source', sa.String(16), nullable=False),
        sa.Column('owner_version', sa.Integer, nullable=False),
        sa.Column('kind', sa.String(16), nullable=False),
        sa.Column('data', sa.JSON, nullable=True))


def downgrade() -> None:
    op.drop_table('big_plan_event')
    op.drop_table('big_plan')
