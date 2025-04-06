"""Gen params are just JSON now for metrics

Revision ID: cb846caea933
Revises: bd2120be1725
Create Date: 2024-01-17 22:22:39.004923

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cb846caea933"
down_revision = "bd2120be1725"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("metric") as batch_op:
        batch_op.add_column(sa.Column("collection_params", sa.JSON, nullable=True))

    op.execute(
        """
        update metric set collection_params = json_object(
            'period', collection_period,
            'eisen', collection_eisen,
            'difficulty', collection_difficulty,
            'actionable_from_day', collection_actionable_from_day,
            'actionable_from_month', collection_actionable_from_month,
            'due_at_time', collection_due_at_time,
            'due_at_day', collection_due_at_day,
            'due_at_month', collection_due_at_month
        )
               where collection_period is not null;
    """
    )

    with op.batch_alter_table("metric") as batch_op:
        batch_op.drop_column("collection_period")
        batch_op.drop_column("collection_eisen")
        batch_op.drop_column("collection_difficulty")
        batch_op.drop_column("collection_actionable_from_day")
        batch_op.drop_column("collection_actionable_from_month")
        batch_op.drop_column("collection_due_at_time")
        batch_op.drop_column("collection_due_at_day")
        batch_op.drop_column("collection_due_at_month")


def downgrade():
    pass
