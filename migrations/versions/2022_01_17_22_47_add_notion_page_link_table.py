"""Add notion page link table

Revision ID: 2e0c08f3893f
Revises: 9b37770abd4d
Create Date: 2022-01-17 22:47:44.072579

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e0c08f3893f'
down_revision = '9b37770abd4d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'notion_page_link',
        sa.Column('the_key', sa.String, primary_key=True),
        sa.Column('notion_id', sa.String, nullable=False),
        sa.Column('created_time', sa.DateTime, nullable=False),
        sa.Column('last_modified_time', sa.DateTime, nullable=False))


def downgrade() -> None:
    op.drop_table('notion_page_link')
