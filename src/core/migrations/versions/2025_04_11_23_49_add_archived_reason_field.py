"""Add archived_reason field

Revision ID: 11e8f1369eb0
Revises: 826b23bc949e
Create Date: 2025-04-11 23:49:45.572347

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "11e8f1369eb0"
down_revision = "826b23bc949e"
branch_labels = None
depends_on = None


# List of all non-_event tables with an 'archived' column
TARGET_TABLES = [
    "auth",
    "big_plan",
    "big_plan_collection",
    "chore",
    "chore_collection",
    "doc",
    "doc_collection",
    "email_task",
    "email_task_collection",
    "gamification_score_log",
    "gamification_score_log_entry",
    "gc_log",
    "gc_log_entry",
    "gen_log",
    "gen_log_entry",
    "habit",
    "habit_collection",
    "inbox_task",
    "inbox_task_collection",
    "journal",
    "journal_collection",
    "metric",
    "metric_collection",
    "metric_entry",
    "note",
    "note_collection",
    "person",
    "person_collection",
    "project",
    "project_collection",
    "push_integration_group",
    "schedule_domain",
    "schedule_event_full_days",
    "schedule_event_in_day",
    "schedule_external_sync_log",
    "schedule_external_sync_log_entry",
    "schedule_stream",
    "slack_task",
    "slack_task_collection",
    "smart_list",
    "smart_list_collection",
    "smart_list_item",
    "smart_list_tag",
    "time_event_domain",
    "time_event_full_days_block",
    "time_event_in_day_block",
    "time_plan",
    "time_plan_activity",
    "time_plan_domain",
    "user",
    "user_workspace_link",
    "vacation",
    "vacation_collection",
    "working_mem",
    "working_mem_collection",
    "workspace",
]


def upgrade() -> None:
    for table in TARGET_TABLES:
        with op.batch_alter_table(table) as batch_op:
            batch_op.add_column(
                sa.Column("archival_reason", sa.String(), nullable=True)
            )
        op.execute(f"UPDATE {table} SET archival_reason = 'user' WHERE archived = 1")


def downgrade() -> None:
    for table in TARGET_TABLES:
        with op.batch_alter_table(table) as batch_op:
            batch_op.drop_column("archival_reason")
