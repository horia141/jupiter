"""Rename docs to doc

Revision ID: f2d273fd9af4
Revises: 9baf42ef5982
Create Date: 2023-12-16 23:21:01.743247

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "f2d273fd9af4"
down_revision = "9baf42ef5982"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
    UPDATE note SET domain = 'doc' WHERE domain = 'docs';
    """
    )


def downgrade() -> None:
    pass
