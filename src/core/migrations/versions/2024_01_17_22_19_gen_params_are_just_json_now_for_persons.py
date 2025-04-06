"""Gen params are just JSON now for persons

Revision ID: bd2120be1725
Revises: e1d79229c3a2
Create Date: 2024-01-17 22:19:00.446509

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bd2120be1725"
down_revision = "e1d79229c3a2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("person") as batch_op:
        batch_op.add_column(sa.Column("catch_up_params", sa.JSON, nullable=True))

    op.execute(
        """
        update person set catch_up_params = json_object(
            'period', catch_up_period,
            'eisen', catch_up_eisen,
            'difficulty', catch_up_difficulty,
            'actionable_from_day', catch_up_actionable_from_day,
            'actionable_from_month', catch_up_actionable_from_month,
            'due_at_time', catch_up_due_at_time,
            'due_at_day', catch_up_due_at_day,
            'due_at_month', catch_up_due_at_month
        )
               where catch_up_period is not null;
    """
    )

    with op.batch_alter_table("person") as batch_op:
        batch_op.drop_column("catch_up_period")
        batch_op.drop_column("catch_up_eisen")
        batch_op.drop_column("catch_up_difficulty")
        batch_op.drop_column("catch_up_actionable_from_day")
        batch_op.drop_column("catch_up_actionable_from_month")
        batch_op.drop_column("catch_up_due_at_time")
        batch_op.drop_column("catch_up_due_at_day")
        batch_op.drop_column("catch_up_due_at_month")


def downgrade():
    pass
