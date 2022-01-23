"""Add recurring task collections table

Revision ID: 7d53547b752f
Revises: efd28a3c8cab
Create Date: 2022-01-15 15:56:26.885592

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d53547b752f'
down_revision = 'efd28a3c8cab'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'recurring_task_collection',
        sa.Column('ref_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('version', sa.Integer, nullable=False),
        sa.Column('archived', sa.Boolean, nullable=False),
        sa.Column('created_time', sa.DateTime, nullable=False),
        sa.Column('last_modified_time', sa.DateTime, nullable=False),
        sa.Column('archived_time', sa.DateTime, nullable=True),
        sa.Column('project_ref_id', sa.Integer, sa.ForeignKey('project.ref_id'), unique=True, index=True, nullable=False))
    op.create_table(
        'recurring_task_collection_event',
        sa.Column('owner_ref_id', sa.Integer, sa.ForeignKey('recurring_task_collection.ref_id'), primary_key=True),
        sa.Column('timestamp', sa.DateTime, primary_key=True),
        sa.Column('session_index', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(32), primary_key=True),
        sa.Column('source', sa.String(16), nullable=False),
        sa.Column('owner_version', sa.Integer, nullable=False),
        sa.Column('kind', sa.String(16), nullable=False),
        sa.Column('data', sa.JSON, nullable=True))


def downgrade() -> None:
    op.drop_table('recurring_task_collection_event')
    op.drop_table('recurring_task_collection')