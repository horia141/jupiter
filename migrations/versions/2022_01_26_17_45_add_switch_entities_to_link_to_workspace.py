"""Add switch entities to link to workspace

Revision ID: 4b3f6afc18d6
Revises: 36b69eee011a
Create Date: 2022-01-26 17:45:05.679309

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b3f6afc18d6'
down_revision = '36b69eee011a'
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
    with op.batch_alter_table('inbox_task_collection', naming_convention=convention) as batch_op:
        batch_op.add_column(sa.Column('workspace_ref_id', sa.Integer, index=True, nullable=True))
        batch_op.create_foreign_key('fk_inbox_task_collection_workspace_ref_id_workspace', 'workspace', ["workspace_ref_id"], ["ref_id"])
        batch_op.drop_index('ix_inbox_task_collection_project_ref_id')
        batch_op.drop_column('project_ref_id')
    with op.batch_alter_table('recurring_task_collection', naming_convention=convention) as batch_op:
        batch_op.add_column(sa.Column('workspace_ref_id', sa.Integer, index=True, nullable=True))
        batch_op.create_foreign_key('fk_recurring_task_collection_workspace_ref_id_workspace', 'workspace', ["workspace_ref_id"], ["ref_id"])
        batch_op.drop_column('project_ref_id')
    with op.batch_alter_table('big_plan_collection', naming_convention=convention) as batch_op:
        batch_op.add_column(sa.Column('workspace_ref_id', sa.Integer, index=True, nullable=True))
        batch_op.create_foreign_key('fk_recurring_task_collection_workspace_ref_id_workspace', 'workspace', ["workspace_ref_id"], ["ref_id"])
        batch_op.drop_index('ix_big_plan_collection_project_ref_id')
        batch_op.drop_column('project_ref_id')


def downgrade() -> None:
    with op.batch_alter_table('inbox_task_collection', naming_convention=convention) as batch_op:
        batch_op.drop_column('workspace_ref_id')
    with op.batch_alter_table('recurring_task_collection', naming_convention=convention) as batch_op:
        batch_op.drop_column('workspace_ref_id')
    with op.batch_alter_table('big_plan_collection', naming_convention=convention) as batch_op:
        batch_op.drop_column('workspace_ref_id')
