"""Add chroes structure

Revision ID: 929c0f592c6e
Revises: a3eccd404042
Create Date: 2022-02-13 15:34:27.062320

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '929c0f592c6e'
down_revision = 'a3eccd404042'
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
    op.create_table(
        'chore_collection',
        sa.Column('ref_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('version', sa.Integer, nullable=False),
        sa.Column('archived', sa.Boolean, nullable=False),
        sa.Column('created_time', sa.DateTime, nullable=False),
        sa.Column('last_modified_time', sa.DateTime, nullable=False),
        sa.Column('archived_time', sa.DateTime, nullable=True),
        sa.Column('workspace_ref_id', sa.Integer, sa.ForeignKey('workspace.ref_id'), unique=True, index=True,
                  nullable=False))
    op.create_table(
        'chore_collection_event',
        sa.Column('owner_ref_id', sa.Integer, sa.ForeignKey('chore_collection.ref_id'), primary_key=True),
        sa.Column('timestamp', sa.DateTime, primary_key=True),
        sa.Column('session_index', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(32), primary_key=True),
        sa.Column('source', sa.String(16), nullable=False),
        sa.Column('owner_version', sa.Integer, nullable=False),
        sa.Column('kind', sa.String(16), nullable=False),
        sa.Column('data', sa.JSON, nullable=True))
    op.create_table(
        'chore',
        sa.Column('ref_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('version', sa.Integer, nullable=False),
        sa.Column('archived', sa.Boolean, nullable=False),
        sa.Column('created_time', sa.DateTime, nullable=False),
        sa.Column('last_modified_time', sa.DateTime, nullable=False),
        sa.Column('archived_time', sa.DateTime, nullable=True),
        sa.Column('chore_collection_ref_id', sa.Integer, sa.ForeignKey("chore_collection.ref_id"),
                  index=True, nullable=False),
        sa.Column('project_ref_id', sa.Integer, sa.ForeignKey('project.ref_id'), nullable=False, index=True),
        sa.Column('name', sa.Unicode(), nullable=False),
        sa.Column('gen_params_period', sa.String, nullable=False),
        sa.Column('gen_params_eisen', sa.String, nullable=True),
        sa.Column('gen_params_difficulty', sa.String, nullable=True),
        sa.Column('gen_params_actionable_from_day', sa.Integer, nullable=True),
        sa.Column('gen_params_actionable_from_month', sa.Integer, nullable=True),
        sa.Column('gen_params_due_at_time', sa.String, nullable=True),
        sa.Column('gen_params_due_at_day', sa.Integer, nullable=True),
        sa.Column('gen_params_due_at_month', sa.Integer, nullable=True),
        sa.Column('suspended', sa.Boolean, nullable=False),
        sa.Column('must_do', sa.Boolean, nullable=False),
        sa.Column('skip_rule', sa.String, nullable=True),
        sa.Column('start_at_date', sa.DateTime, nullable=False),
        sa.Column('end_at_date', sa.DateTime, nullable=True), )
    op.create_table(
        'chore_event',
        sa.Column('owner_ref_id', sa.Integer, sa.ForeignKey('chore.ref_id'), primary_key=True),
        sa.Column('timestamp', sa.DateTime, primary_key=True),
        sa.Column('session_index', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(32), primary_key=True),
        sa.Column('source', sa.String(16), nullable=False),
        sa.Column('owner_version', sa.Integer, nullable=False),
        sa.Column('kind', sa.String(16), nullable=False),
        sa.Column('data', sa.JSON, nullable=True))
    with op.batch_alter_table('inbox_task', naming_convention=convention) as batch_op:
        batch_op.add_column(sa.Column('chore_ref_id', sa.Integer, index=True, nullable=True))
        batch_op.create_foreign_key('fk_inbox_task_chore_ref_id_chore', 'chore', ["chore_ref_id"], ["ref_id"])


def downgrade() -> None:
    op.drop_table('recurring_task_event')
    op.drop_table('recurring_task')
    op.drop_table('chore_collection_event')
    op.drop_table('chore_collection')
