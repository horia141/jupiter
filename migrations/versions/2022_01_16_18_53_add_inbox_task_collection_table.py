"""Add inbox task collection table

Revision ID: bd7279dd5af1
Revises: 500745bf02b0
Create Date: 2022-01-16 18:53:37.011907

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd7279dd5af1'
down_revision = '500745bf02b0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'inbox_task_collection',
        sa.Column('ref_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('version', sa.Integer, nullable=False),
        sa.Column('archived', sa.Boolean, nullable=False),
        sa.Column('created_time', sa.DateTime, nullable=False),
        sa.Column('last_modified_time', sa.DateTime, nullable=False),
        sa.Column('archived_time', sa.DateTime, nullable=True),
        sa.Column('project_ref_id', sa.Integer, sa.ForeignKey('project.ref_id'), unique=True, index=True, nullable=False))
    op.create_table(
        'inbox_task_collection_event',
        sa.Column('owner_ref_id', sa.Integer, sa.ForeignKey('inbox_task_collection.ref_id'), primary_key=True),
        sa.Column('timestamp', sa.DateTime, primary_key=True),
        sa.Column('session_index', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(32), primary_key=True),
        sa.Column('source', sa.String(16), nullable=False),
        sa.Column('owner_version', sa.Integer, nullable=False),
        sa.Column('kind', sa.String(16), nullable=False),
        sa.Column('data', sa.JSON, nullable=True))


def downgrade() -> None:
    op.drop_table('inbox_task_collection_event')
    op.drop_table('inbox_task_collection')
