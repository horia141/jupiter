"""Add smart list tags table

Revision ID: 758d7a35b604
Revises: b499a7eca9e2
Create Date: 2022-01-14 21:01:34.188632

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '758d7a35b604'
down_revision = 'b499a7eca9e2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'smart_list_tag',
        sa.Column('ref_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('version', sa.Integer, nullable=False),
        sa.Column('archived', sa.Boolean, nullable=False),
        sa.Column('created_time', sa.DateTime, nullable=False),
        sa.Column('last_modified_time', sa.DateTime, nullable=False),
        sa.Column('archived_time', sa.DateTime, nullable=True),
        sa.Column('smart_list_ref_id', sa.Integer, sa.ForeignKey('smart_list.ref_id'), index=True, nullable=False),
        sa.Column('tag_name', sa.String(100), nullable=False))
    op.create_table(
        'smart_list_tag_event',
        sa.Column('owner_ref_id', sa.Integer, sa.ForeignKey('smart_list_tag.ref_id'), primary_key=True),
        sa.Column('timestamp', sa.DateTime, primary_key=True),
        sa.Column('session_index', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(32), primary_key=True),
        sa.Column('source', sa.String(16), nullable=False),
        sa.Column('owner_version', sa.Integer, nullable=False),
        sa.Column('kind', sa.String(16), nullable=False),
        sa.Column('data', sa.JSON, nullable=True))


def downgrade() -> None:
    op.drop_table('smart_list_tag_event')
    op.drop_table('smart_list_tag')
