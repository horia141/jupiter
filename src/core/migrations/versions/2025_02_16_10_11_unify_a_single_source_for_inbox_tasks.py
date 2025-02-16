"""Unify a single source for inbox tasks

Revision ID: 312347a664ec
Revises: 5c4e136dcace
Create Date: 2025-02-16 10:11:02.013997

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "312347a664ec"
down_revision = "5c4e136dcace"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add the new nullable column
    with op.batch_alter_table("inbox_task") as batch_op:
        bind = op.get_bind()
        insp = sa.inspect(bind)
        columns = insp.get_columns("inbox_task")
        if "source_entity_ref_id" not in [column["name"] for column in columns]:
            batch_op.add_column(
                sa.Column("source_entity_ref_id", sa.Integer(), nullable=True)
            )

    op.execute(
        """CREATE INDEX ix_inbox_task_source_entity_ref_id ON inbox_task (source_entity_ref_id) WHERE source_entity_ref_id IS NOT NULL"""
    )
    # Backfill the new column
    op.execute(
        """
        UPDATE inbox_task
        SET source_entity_ref_id = COALESCE(
            working_mem_ref_id,
            habit_ref_id,
            chore_ref_id,
            big_plan_ref_id,
            journal_ref_id,
            metric_ref_id,
            person_ref_id,
            email_task_ref_id,
            slack_task_ref_id
        )
    """
    )

    # Drop the old columns
    try:
        with op.batch_alter_table("inbox_task") as batch_op:
            batch_op.drop_index("ix_inbox_task_working_mem_ref_id")
            batch_op.drop_column("working_mem_ref_id")
        with op.batch_alter_table("inbox_task") as batch_op:
            batch_op.drop_index("ix_inbox_task_habit_ref_id")
            batch_op.drop_column("habit_ref_id")
        with op.batch_alter_table("inbox_task") as batch_op:
            batch_op.drop_index("ix_inbox_task_chore_ref_id")
            batch_op.drop_column("chore_ref_id")
        with op.batch_alter_table("inbox_task") as batch_op:
            batch_op.drop_index("ix_inbox_task_big_plan_ref_id")
            batch_op.drop_column("big_plan_ref_id")
        with op.batch_alter_table("inbox_task") as batch_op:
            batch_op.drop_index("ix_inbox_task_journal_ref_id")
            batch_op.drop_column("journal_ref_id")
        with op.batch_alter_table("inbox_task") as batch_op:
            batch_op.drop_index("ix_inbox_task_metric_ref_id")
            batch_op.drop_column("metric_ref_id")
        with op.batch_alter_table("inbox_task") as batch_op:
            batch_op.drop_index("ix_inbox_task_person_ref_id")
            batch_op.drop_column("person_ref_id")
        with op.batch_alter_table("inbox_task") as batch_op:
            batch_op.drop_index("ix_inbox_task_email_task_ref_id")
            batch_op.drop_column("email_task_ref_id")
        with op.batch_alter_table("inbox_task") as batch_op:
            batch_op.drop_index("ix_inbox_task_slack_task_ref_id")
            batch_op.drop_column("slack_task_ref_id")
    except KeyError as e:
        pass


def downgrade() -> None:
    pass
