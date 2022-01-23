"""Add Notion connection table

Revision ID: c1db7da45ef5
Revises: a5a0a1e400dd
Create Date: 2022-01-22 21:39:49.336624

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1db7da45ef5'
down_revision = 'a5a0a1e400dd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'notion_connection',
        sa.Column('ref_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('version', sa.Integer, nullable=False),
        sa.Column('archived', sa.Boolean, nullable=False),
        sa.Column('created_time', sa.DateTime, nullable=False),
        sa.Column('last_modified_time', sa.DateTime, nullable=False),
        sa.Column('archived_time', sa.DateTime, nullable=True),
        sa.Column('workspace_ref_id', sa.Integer, sa.ForeignKey('workspace.ref_id'), index=True, unique=True, nullable=False),
        sa.Column('space_id', sa.String, nullable=False),
        sa.Column('token', sa.String, nullable=False))
    op.create_table(
        'notion_connection_event',
        sa.Column('owner_ref_id', sa.Integer, sa.ForeignKey('notion_connection.ref_id'), primary_key=True),
        sa.Column('timestamp', sa.DateTime, primary_key=True),
        sa.Column('session_index', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(32), primary_key=True),
        sa.Column('source', sa.String(16), nullable=False),
        sa.Column('owner_version', sa.Integer, nullable=False),
        sa.Column('kind', sa.String(16), nullable=False),
        sa.Column('data', sa.JSON, nullable=True))


def downgrade() -> None:
    op.drop_table('notion_connection_event')
    op.drop_table('notion_connection')
