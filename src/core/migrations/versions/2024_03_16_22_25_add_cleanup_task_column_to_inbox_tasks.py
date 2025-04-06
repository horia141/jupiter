"""Add cleanup task column to inbox tasks

Revision ID: e57d34a43026
Revises: 9dd1fba9fd4e
Create Date: 2024-03-16 22:25:15.292552

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e57d34a43026"
down_revision = "9dd1fba9fd4e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    naming_convention = {
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
    with op.batch_alter_table(
        "inbox_task", naming_convention=naming_convention
    ) as batch_op:
        batch_op.add_column(sa.Column("working_mem_ref_id", sa.Integer))
        batch_op.create_foreign_key(
            "fk_inbox_task_working_mem_ref_id_working_mem",
            "working_mem",
            ["working_mem_ref_id"],
            ["ref_id"],
        )
    op.execute(
        """
        CREATE INDEX ix_inbox_task_working_mem_ref_id ON inbox_task (working_mem_ref_id);"""
    )


def downgrade() -> None:
    pass
