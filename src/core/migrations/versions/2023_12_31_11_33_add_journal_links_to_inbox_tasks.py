"""Add journal links to inbox tasks

Revision ID: 2f7390ee2ae2
Revises: 760292ab1a52
Create Date: 2023-12-31 11:33:36.206887

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2f7390ee2ae2"
down_revision = "760292ab1a52"
branch_labels = None
depends_on = None


def upgrade() -> None:
    naming_convention = {
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
    with op.batch_alter_table(
        "inbox_task", naming_convention=naming_convention
    ) as batch_op:
        batch_op.add_column(sa.Column("journal_ref_id", sa.Integer))
        batch_op.create_foreign_key(
            "fk_inbox_task_journal_ref_id_journal",
            "journal",
            ["journal_ref_id"],
            ["ref_id"],
        )
    op.execute(
        """
        CREATE INDEX ix_inbox_task_journal_ref_id ON inbox_task (journal_ref_id);"""
    )


def downgrade():
    pass
