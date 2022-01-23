"""Add notion collection item link table

Revision ID: e513f62cebb5
Revises: 06636bccb6f1
Create Date: 2022-01-20 23:40:24.295032

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e513f62cebb5'
down_revision = '06636bccb6f1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'notion_collection_item_link',
        sa.Column('the_key', sa.String, primary_key=True),
        sa.Column('collection_key', sa.String, sa.ForeignKey('notion_collection_link.the_key'), index=True, nullable=False),
        sa.Column('ref_id', sa.String, nullable=False),
        sa.Column('notion_id', sa.String, nullable=False),
        sa.Column('created_time', sa.DateTime, nullable=False),
        sa.Column('last_modified_time', sa.DateTime, nullable=False))


def downgrade() -> None:
    op.drop_table('notion_collection_item_link')
