"""Add fields for journals

Revision ID: 7179356b640d
Revises: 027799f464d5
Create Date: 2025-04-23 16:28:06.022898

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7179356b640d'
down_revision = '027799f464d5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    naming_convention = {
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
    with op.batch_alter_table(
        "journal_collection", naming_convention=naming_convention
    ) as batch_op:
        batch_op.add_column(
            sa.Column("generation_approach", sa.String(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("generation_in_advance_days", sa.JSON(), nullable=True)
        )

    op.execute(
        """
        UPDATE journal_collection SET writing_task_project_ref_id=NULL where writing_task_project_ref_id is NULL
    """
    )
    op.execute(
        """
        UPDATE journal_collection SET generation_approach='both-journal-and-task' where generation_approach is NULL
    """
    )
    op.execute(
        """
        UPDATE journal_collection SET generation_in_advance_days='{"quarterly": 14, "weekly": 3}' where generation_in_advance_days is NULL
    """
    )
        


def downgrade() -> None:
    pass
