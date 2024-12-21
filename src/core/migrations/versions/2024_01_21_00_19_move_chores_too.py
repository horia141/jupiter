"""Move chores too

Revision ID: 493273686d33
Revises: a4aad54ad575
Create Date: 2024-01-21 00:19:50.267031

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "493273686d33"
down_revision = "a4aad54ad575"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("chore") as batch_op:
        batch_op.add_column(sa.Column("gen_params", sa.JSON, nullable=True))

    op.execute(
        """
        update chore set gen_params = json_object(
            'period', gen_params_period,
            'eisen', gen_params_eisen,
            'difficulty', gen_params_difficulty,
            'actionable_from_day', gen_params_actionable_from_day,
            'actionable_from_month', gen_params_actionable_from_month,
            'due_at_time', gen_params_due_at_time,
            'due_at_day', gen_params_due_at_day,
            'due_at_month', gen_params_due_at_month
        )
               where gen_params_period is not null;
    """
    )

    with op.batch_alter_table("chore") as batch_op:
        batch_op.drop_column("gen_params_period")
        batch_op.drop_column("gen_params_eisen")
        batch_op.drop_column("gen_params_difficulty")
        batch_op.drop_column("gen_params_actionable_from_day")
        batch_op.drop_column("gen_params_actionable_from_month")
        batch_op.drop_column("gen_params_due_at_time")
        batch_op.drop_column("gen_params_due_at_day")
        batch_op.drop_column("gen_params_due_at_month")


def downgrade() -> None:
    pass
