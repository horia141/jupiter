"""Add project ref id to entities

Revision ID: 36b69eee011a
Revises: f81984d09e7d
Create Date: 2022-01-25 22:27:45.574362

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '36b69eee011a'
down_revision = 'f81984d09e7d'
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
        batch_op.add_column(sa.Column('project_ref_id', sa.Integer, index=True, nullable=True))
        batch_op.create_foreign_key('fk_inbox_task_project_ref_id_project', 'project', ["project_ref_id"], ["ref_id"])
    with op.batch_alter_table('recurring_task', naming_convention=convention) as batch_op:
        batch_op.add_column(sa.Column('project_ref_id', sa.Integer, index=True, nullable=True))
        batch_op.create_foreign_key('fk_recurring_task_project_ref_id_project', 'project', ["project_ref_id"], ["ref_id"])
    with op.batch_alter_table('big_plan', naming_convention=convention) as batch_op:
        batch_op.add_column(sa.Column('project_ref_id', sa.Integer, index=True, nullable=True))
        batch_op.create_foreign_key('fk_big_plan_project_ref_id_project', 'project', ["project_ref_id"], ["ref_id"])


def downgrade() -> None:
    with op.batch_alter_table('inbox_task', naming_convention=convention) as batch_op:
        batch_op.drop_column('project_ref_id')
    with op.batch_alter_table('recurring_task', naming_convention=convention) as batch_op:
        batch_op.drop_column('project_ref_id')
    with op.batch_alter_table('big_plan', naming_convention=convention) as batch_op:
        batch_op.drop_column('project_ref_id')
