"""Modify inbox tasks with column

Revision ID: 04fc03a337b3
Revises: 699090c0908a
Create Date: 2022-03-24 23:20:08.308653

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '04fc03a337b3'
down_revision = '699090c0908a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    naming_convention = {
        "fk":
            "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
    with op.batch_alter_table("inbox_task", naming_convention=naming_convention) as batch_op:
        batch_op.add_column(sa.Column('slack_task_ref_id', sa.Integer))
        batch_op.create_foreign_key("fk_inbox_task_slack_task_ref_id_slack_task", "slack_task", ["slack_task_ref_id"], ["ref_id"])
    op.execute("""
        CREATE INDEX ix_inbox_task_slack_task_ref_id ON inbox_task (slack_task_ref_id);""")


def downgrade() -> None:
    pass
