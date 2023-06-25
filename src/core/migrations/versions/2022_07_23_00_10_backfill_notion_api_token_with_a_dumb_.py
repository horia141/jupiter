"""Backfill Notion API token with a dumb value

Revision ID: 8762c5103041
Revises: c115e4c4a657
Create Date: 2022-07-23 00:10:44.695419

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "8762c5103041"
down_revision = "c115e4c4a657"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """update notion_connection set api_token='secret_badtokenpleaseprovidevalue'"""
    )


def downgrade():
    pass
