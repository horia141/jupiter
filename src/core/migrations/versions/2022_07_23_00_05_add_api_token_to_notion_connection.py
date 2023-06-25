"""Add API token to Notion connection

Revision ID: c115e4c4a657
Revises: e8fd0eb71871
Create Date: 2022-07-23 00:05:32.431686

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c115e4c4a657"
down_revision = "e8fd0eb71871"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "notion_connection", sa.Column("api_token", sa.String(), nullable=True)
    )


def downgrade() -> None:
    pass
