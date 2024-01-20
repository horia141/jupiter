"""Migrate journal collections ofc

Revision ID: 9a2848c9a2e4
Revises: 37dd9d715387
Create Date: 2024-01-20 21:18:52.012147

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a2848c9a2e4'
down_revision = '37dd9d715387'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("journal_collection") as batch_op:
        batch_op.add_column(sa.Column("writing_task_gen_params", sa.JSON, nullable=True))

    op.execute(
        """
        update journal_collection set writing_task_gen_params = json_object(
            'period', 'daily',
            'eisen', writing_task_eisen,
            'difficulty', writing_task_difficulty,
            'actionable_from_day', null,
            'actionable_from_month', null,
            'due_at_time', null,
            'due_at_day', null,
            'due_at_month', null
        )
    """
    )

    with op.batch_alter_table("journal_collection") as batch_op:
        batch_op.drop_column("writing_task_eisen")
        batch_op.drop_column("writing_task_difficulty")


def downgrade() -> None:
    pass
