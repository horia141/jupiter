"""Drop Notion tables

Revision ID: 7e8c0bc468ca
Revises: d25373054629
Create Date: 2023-04-21 00:08:36.709657

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "7e8c0bc468ca"
down_revision = "d25373054629"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("drop table if exists notion_connection")
    op.execute("drop table if exists notion_connection_event")
    op.execute("drop table if exists notion_page_link")
    op.execute("drop table if exists notion_collection_link")
    op.execute("drop table if exists notion_collection_field_tag_link")
    op.execute("drop table if exists notion_collection_item_link")


def downgrade():
    pass
