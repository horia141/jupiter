"""Add notion collection link table

Revision ID: 3d59562f6736
Revises: 2e0c08f3893f
Create Date: 2022-01-19 23:32:30.852802

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d59562f6736'
down_revision = '2e0c08f3893f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'notion_collection_link',
        sa.Column('the_key', sa.String, primary_key=True),
        sa.Column('page_notion_id', sa.String, nullable=False),
        sa.Column('collection_notion_id', sa.String, nullable=False),
        sa.Column('view_notion_ids', sa.JSON, nullable=False),
        sa.Column('created_time', sa.DateTime, nullable=False),
        sa.Column('last_modified_time', sa.DateTime, nullable=False))


def downgrade() -> None:
    op.drop_table('notion_collection_link')
