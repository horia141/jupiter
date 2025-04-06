"""Backfill notes properties

Revision ID: 2bec03c27977
Revises: 98898cddadae
Create Date: 2023-11-26 10:46:19.572410

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "2bec03c27977"
down_revision = "98898cddadae"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE workspace
        SET feature_flags = json_set(feature_flags, '$.notes', 'true')
        """
    )


def downgrade() -> None:
    pass
