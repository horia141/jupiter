"""Relax constraints on time plans

Revision ID: ea359cf44393
Revises: 2be36a76f15d
Create Date: 2024-06-01 20:42:47.967135

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "ea359cf44393"
down_revision = "2be36a76f15d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""DROP INDEX ix_time_plan_time_plan_domain_ref_id_right_now""")
    op.execute(
        """
        CREATE UNIQUE INDEX ix_time_plan_time_plan_domain_ref_id_period_right_now ON time_plan (time_plan_domain_ref_id, period, right_now)
        WHERE archived=0;
    """
    )


def downgrade() -> None:
    pass
