"""Add metric collection table

Revision ID: 73a00d90c1ff
Revises: 6a122bdc1691
Create Date: 2022-01-31 16:01:48.875456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73a00d90c1ff'
down_revision = '6a122bdc1691'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'metric_collection',
        sa.Column('ref_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('version', sa.Integer, nullable=False),
        sa.Column('archived', sa.Boolean, nullable=False),
        sa.Column('created_time', sa.DateTime, nullable=False),
        sa.Column('last_modified_time', sa.DateTime, nullable=False),
        sa.Column('archived_time', sa.DateTime, nullable=True),
        sa.Column('workspace_ref_id', sa.Integer, sa.ForeignKey('workspace.ref_id'), unique=True, index=True, nullable=False),
        sa.Column('collection_project_ref_id', sa.Integer, nullable=False))
    op.create_table(
        'metric_collection_event',
        sa.Column('owner_ref_id', sa.Integer, sa.ForeignKey('metric_collection.ref_id'), primary_key=True),
        sa.Column('timestamp', sa.DateTime, primary_key=True),
        sa.Column('session_index', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(32), primary_key=True),
        sa.Column('source', sa.String(16), nullable=False),
        sa.Column('owner_version', sa.Integer, nullable=False),
        sa.Column('kind', sa.String(16), nullable=False),
        sa.Column('data', sa.JSON, nullable=True))


def downgrade() -> None:
    op.drop_table('metric_collection_event')
    op.drop_table('metric_collection')
