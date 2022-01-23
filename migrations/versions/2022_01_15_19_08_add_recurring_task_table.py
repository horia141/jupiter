"""Add recurring task table

Revision ID: 4df0e666abd6
Revises: 7d53547b752f
Create Date: 2022-01-15 19:08:00.141081

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4df0e666abd6'
down_revision = '7d53547b752f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'recurring_task',
        sa.Column('ref_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('version', sa.Integer, nullable=False),
        sa.Column('archived', sa.Boolean, nullable=False),
        sa.Column('created_time', sa.DateTime, nullable=False),
        sa.Column('last_modified_time', sa.DateTime, nullable=False),
        sa.Column('archived_time', sa.DateTime, nullable=True),
        sa.Column('recurring_task_collection_ref_id', sa.Integer, sa.ForeignKey("recurring_task_collection.ref_id"), index=True, nullable=False),
        sa.Column('name', sa.Unicode(), nullable=False),
        sa.Column('the_type', sa.String(16), nullable=False),
        sa.Column('gen_params_project_ref_id', sa.Integer, sa.ForeignKey('project.ref_id'), nullable=False),
        sa.Column('gen_params_period', sa.String, nullable=False),
        sa.Column('gen_params_eisen', sa.String, nullable=True),
        sa.Column('gen_params_difficulty', sa.String, nullable=True),
        sa.Column('gen_params_actionable_from_day', sa.Integer, nullable=True),
        sa.Column('gen_params_actionable_from_month', sa.Integer, nullable=True),
        sa.Column('gen_params_due_at_time', sa.String, nullable=True),
        sa.Column('gen_params_due_at_day', sa.Integer, nullable=True),
        sa.Column('gen_params_due_at_month', sa.Integer, nullable=True),
        sa.Column('suspended', sa.Boolean, nullable=False),
        sa.Column('skip_rule', sa.String, nullable=True),
        sa.Column('must_do', sa.Boolean, nullable=False),
        sa.Column('start_at_date', sa.DateTime, nullable=False),
        sa.Column('end_at_date', sa.DateTime, nullable=True),)
    op.create_table(
        'recurring_task_event',
        sa.Column('owner_ref_id', sa.Integer, sa.ForeignKey('recurring_task.ref_id'), primary_key=True),
        sa.Column('timestamp', sa.DateTime, primary_key=True),
        sa.Column('session_index', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(32), primary_key=True),
        sa.Column('source', sa.String(16), nullable=False),
        sa.Column('owner_version', sa.Integer, nullable=False),
        sa.Column('kind', sa.String(16), nullable=False),
        sa.Column('data', sa.JSON, nullable=True))


def downgrade() -> None:
    op.drop_table('recurring_task_event')
    op.drop_table('recurring_task')
