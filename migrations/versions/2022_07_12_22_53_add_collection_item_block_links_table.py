"""Add collection item block links table

Revision ID: e8fd0eb71871
Revises: d9629228f17e
Create Date: 2022-07-12 22:53:02.329951

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8fd0eb71871'
down_revision = 'd9629228f17e'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    CREATE TABLE IF NOT EXISTS notion_collection_item_block_link (
        item_key VARCHAR NOT NULL,
        position INTEGER NOT NULL,
        collection_key VARCHAR NOT NULL, 
        the_type VARCHAR NOT NULL, 
        notion_id VARCHAR NOT NULL, 
        created_time DATETIME NOT NULL, 
        last_modified_time DATETIME NOT NULL, 
        PRIMARY KEY (item_key, position), 
        FOREIGN KEY (item_key) REFERENCES notion_collection_item_link (the_key)
        FOREIGN KEY(collection_key) REFERENCES notion_collection_link (the_key)
    );""")
    op.execute("""
    CREATE INDEX ix_notion_collection_item_block_link_item_key ON notion_collection_item_block_link (item_key);""")
    op.execute("""
    CREATE INDEX ix_notion_collection_item_block_link_collection_key ON notion_collection_item_block_link (collection_key);""")


def downgrade():
    op.execute("""DROP TABLE notion_collection_item_block_link""")
