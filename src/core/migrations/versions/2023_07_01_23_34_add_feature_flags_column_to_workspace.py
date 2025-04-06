"""Add feature flags column to workspace

Revision ID: 89c2a987db66
Revises: fee96a64dd68
Create Date: 2023-07-01 23:34:35.536226

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "89c2a987db66"
down_revision = "fee96a64dd68"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("workspace") as batch_op:
        batch_op.add_column(sa.Column("feature_flags", sa.JSON))
    op.execute(
        """update workspace set feature_flags='{"inbox-tasks": true, "habits": true, "chores": true, "big-plans": true, "vacations": true, "projects": true, "smart-lists": true, "metrics": true, "persons": true, "slack-tasks": false, "email-tasks": false}'"""
    )
    with op.batch_alter_table("workspace") as batch_op:
        batch_op.alter_column("feature_flags", existing_type=sa.JSON, nullable=False)


def downgrade():
    pass
