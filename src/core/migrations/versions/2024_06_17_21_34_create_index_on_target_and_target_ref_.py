"""Create index on target and target_ref_id for time plans

Revision ID: 94535a7e2a28
Revises: ea359cf44393
Create Date: 2024-06-17 21:34:31.876692

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "94535a7e2a28"
down_revision = "ea359cf44393"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX ix_time_plan_activity_target_target_ref_id ON time_plan_activity (target, target_ref_id)
    """
    )


def downgrade() -> None:
    pass
