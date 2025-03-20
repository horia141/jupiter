"""Backup feature working mem

Revision ID: 626b770f8db6
Revises: e57d34a43026
Create Date: 2024-03-21 00:44:23.130986

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "626b770f8db6"
down_revision = "e57d34a43026"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE workspace
        SET feature_flags = json_set(feature_flags, '$.working-mem', 'true')
        """
    )


def downgrade() -> None:
    pass
