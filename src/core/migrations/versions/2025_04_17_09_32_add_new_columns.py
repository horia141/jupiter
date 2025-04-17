"""Add new columns

Revision ID: 027799f464d5
Revises: 11e8f1369eb0
Create Date: 2025-04-17 09:32:51.119279

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '027799f464d5'
down_revision = '11e8f1369eb0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    naming_convention = {
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
    with op.batch_alter_table("time_plan_domain", naming_convention=naming_convention) as batch_op:
        batch_op.add_column(sa.Column("periods", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("planning_task_project_ref_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("planning_task_gen_params", sa.JSON(), nullable=True))
        batch_op.create_foreign_key(
            "fk_time_plan_domain_planning_task_project_ref_id_project",
            "project",
            ["planning_task_project_ref_id"],
            ["ref_id"]
        )
        # batch_op.drop_column("days_until_gc")

    op.execute("""
        UPDATE time_plan_domain SET periods='["weekly"]' where periods is NULL
    """)
    op.execute("""
        UPDATE time_plan_domain SET planning_task_gen_params=json_object(
            'period', 'daily',
            'eisen', 'important',
            'difficulty', 'medium',
            'actionable_from_day', null,
            'actionable_from_month', null,
            'due_at_time', null,
            'due_at_day', null,
            'due_at_month', null,
            'skip_rule', null
        ) where planning_task_gen_params is NULL
    """)
    op.execute("""
        INSERT INTO time_plan_domain
        SELECT
            td.ref_id + 10000 as ref_id,
            td.version as version,
            td.archived as archived,
            td.created_time as created_time,
            td.last_modified_time as last_modified_time,
            td.archived_time as archived_time,
            td.workspace_ref_id + 10000 as workspace_ref_id,
            td.archival_reason as archival_reason,
            td.periods as persiods,
            p.ref_id as planning_task_project_ref_id,
            td.planning_task_gen_params as planning_task_gen_params
        FROM time_plan_domain td 
        JOIN workspace w 
        ON td.workspace_ref_id=w.ref_id
        JOIN project_collection pc 
        ON pc.workspace_ref_id=w.ref_id 
        JOIN (
            SELECT 
                ref_id,
                project_collection_ref_id
            FROM project
            WHERE parent_project_ref_id 
            IS NULL) as p
        ON p.project_collection_ref_id=pc.ref_id;
    """)
    op.execute("""
        DELETE FROM time_plan_domain WHERE planning_task_project_ref_id IS NULL
    """)
    op.execute("""
        UPDATE time_plan_domain SET workspace_ref_id=workspace_ref_id-10000
    """)

def downgrade() -> None:
    pass
