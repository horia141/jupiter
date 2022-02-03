"""Add projects table


Revision ID: c7d76ff55cea
Revises: 016859689ec3
Create Date: 2022-01-13 23:17:45.093261

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7d76ff55cea'
down_revision = '016859689ec3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'project',
        sa.Column('ref_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('version', sa.Integer, nullable=False),
        sa.Column('archived', sa.Boolean, nullable=False),
        sa.Column('created_time', sa.DateTime, nullable=False),
        sa.Column('last_modified_time', sa.DateTime, nullable=False),
        sa.Column('archived_time', sa.DateTime, nullable=True),
        sa.Column('project_collection_ref_id', sa.Integer, sa.ForeignKey('project_collection.ref_id'), index=True, nullable=False),
        sa.Column('the_key', sa.String(32), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('notion_link_uuid', sa.String(16), nullable=False))
    op.create_table(
        'project_event',
        sa.Column('owner_ref_id', sa.Integer, sa.ForeignKey('project.ref_id'), primary_key=True),
        sa.Column('timestamp', sa.DateTime, primary_key=True),
        sa.Column('session_index', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(32), primary_key=True),
        sa.Column('source', sa.String(16), nullable=False),
        sa.Column('owner_version', sa.Integer, nullable=False),
        sa.Column('kind', sa.String(16), nullable=False),
        sa.Column('data', sa.JSON, nullable=True))


def downgrade() -> None:
    op.drop_table('project_event')
    op.drop_table('project')
