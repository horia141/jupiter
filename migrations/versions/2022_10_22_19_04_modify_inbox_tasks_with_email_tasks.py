"""Modify inbox tasks with email tasks

Revision ID: d25373054629
Revises: 2e90eb234797
Create Date: 2022-10-22 19:04:19.710859

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'd25373054629'
down_revision = '2e90eb234797'
branch_labels = None
depends_on = None


def upgrade():
    naming_convention = {
        "fk":
            "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
    with op.batch_alter_table("inbox_task", naming_convention=naming_convention) as batch_op:
        batch_op.add_column(sa.Column('email_task_ref_id', sa.Integer))
        batch_op.create_foreign_key("fk_inbox_task_email_task_ref_id_email_task", "email_task", ["email_task_ref_id"],
                                    ["ref_id"])
    op.execute("""
            CREATE INDEX ix_inbox_task_email_task_ref_id ON inbox_task (email_task_ref_id);""")


def downgrade():
    pass
