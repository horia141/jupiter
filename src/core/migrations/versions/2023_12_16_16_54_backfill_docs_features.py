"""Backfill docs features

Revision ID: 9baf42ef5982
Revises: d6e189bbdc0a
Create Date: 2023-12-16 16:54:05.184713

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "9baf42ef5982"
down_revision = "d6e189bbdc0a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE workspace
        SET feature_flags = json_set(feature_flags, '$.docs', 'true')
        """
    )
    op.execute(
        """
        UPDATE workspace
        SET feature_flags = json_remove(feature_flags, '$.notes')
        """
    )


def downgrade() -> None:
    pass
