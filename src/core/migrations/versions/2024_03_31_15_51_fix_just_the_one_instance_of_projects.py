"""Fix just the one instance of projects

Revision ID: 6dd9a9a34fa8
Revises: 97aa6c5f0c4b
Create Date: 2024-03-31 15:51:33.063379

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "6dd9a9a34fa8"
down_revision = "97aa6c5f0c4b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE project
        SET order_of_child_projects = "[0, 16, 20, 21 , 22, 23, 24]"
        WHERE ref_id = 1001
        AND name = "Life AXA"
    """
    )


def downgrade() -> None:
    pass
