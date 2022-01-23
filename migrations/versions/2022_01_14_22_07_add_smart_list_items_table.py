"""Add smart list items table

Revision ID: efd28a3c8cab
Revises: 758d7a35b604
Create Date: 2022-01-14 22:07:59.396983

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'efd28a3c8cab'
down_revision = '758d7a35b604'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'smart_list_item',
        sa.Column('ref_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('version', sa.Integer, nullable=False),
        sa.Column('archived', sa.Boolean, nullable=False),
        sa.Column('created_time', sa.DateTime, nullable=False),
        sa.Column('last_modified_time', sa.DateTime, nullable=False),
        sa.Column('archived_time', sa.DateTime, nullable=True),
        sa.Column('smart_list_ref_id', sa.Integer, sa.ForeignKey('smart_list.ref_id'), index=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('is_done', sa.Boolean, nullable=False),
        sa.Column('tags_ref_id', sa.JSON, nullable=False),
        sa.Column('url', sa.String, nullable=True))
    op.create_table(
        'smart_list_item_event',
        sa.Column('owner_ref_id', sa.Integer, sa.ForeignKey('smart_list.ref_id'), primary_key=True),
        sa.Column('timestamp', sa.DateTime, primary_key=True),
        sa.Column('session_index', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(32), primary_key=True),
        sa.Column('source', sa.String(16), nullable=False),
        sa.Column('owner_version', sa.Integer, nullable=False),
        sa.Column('kind', sa.String(16), nullable=False),
        sa.Column('data', sa.JSON, nullable=True))


def downgrade() -> None:
    op.drop_table('smart_list_item_event')
    op.drop_table('smart_list_item')
