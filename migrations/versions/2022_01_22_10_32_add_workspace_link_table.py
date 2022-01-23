"""Add workspace link table

Revision ID: c99c4f461753
Revises: e513f62cebb5
Create Date: 2022-01-22 10:32:25.311132

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c99c4f461753'
down_revision = 'e513f62cebb5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'notion_workspace_link',
        sa.Column('workspace_ref_id', sa.Integer, sa.ForeignKey('workspace.ref_id'), primary_key=True),
        sa.Column('notion_id', sa.String, nullable=False),
        sa.Column('created_time', sa.DateTime, nullable=False),
        sa.Column('last_modified_time', sa.DateTime, nullable=False))


def downgrade() -> None:
    op.drop_table('notion_workspace_link')
