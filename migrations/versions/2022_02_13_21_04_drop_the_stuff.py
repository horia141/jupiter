"""Drop the stuff

Revision ID: 82a9343cb654
Revises: 929c0f592c6e
Create Date: 2022-02-13 21:04:01.385605

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '82a9343cb654'
down_revision = '929c0f592c6e'
branch_labels = None
depends_on = None


convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


def upgrade() -> None:
    with op.batch_alter_table('inbox_task', naming_convention=convention) as batch_op:
        batch_op.drop_index('ix_inbox_task_recurring_task_ref_id')
        batch_op.drop_column('recurring_task_ref_id')
    op.drop_table('recurring_task')
    op.drop_table('recurring_task_event')


def downgrade() -> None:
    pass
