"""Add search tables

Revision ID: fbdcd37bbdae
Revises: 89c2a987db66
Create Date: 2023-08-05 16:36:38.553198

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "fbdcd37bbdae"
down_revision = "89c2a987db66"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
    CREATE VIRTUAL TABLE search_index USING fts5(
        workspace_ref_id,
        entity_tag,
        ref_id UNINDEXED, 
        name,
        archived UNINDEXED,
        tokenize="porter unicode61 remove_diacritics 1"
    );
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'InboxTask' as entity_tag,
        e.ref_id as ref_id,
        e.name as name,
        e.archived AS archived
    FROM inbox_task_collection AS c
    JOIN inbox_task AS e
    ON c.ref_id=e.inbox_task_collection_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'Habit' as entity_tag,
        e.ref_id as ref_id,
        e.name as name,
        e.archived AS archived
    FROM habit_collection AS c
    JOIN habit AS e
    ON c.ref_id=e.habit_collection_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'Chore' as entity_tag,
        e.ref_id as ref_id,
        e.name as name,
        e.archived AS archived
    FROM chore_collection AS c
    JOIN chore AS e
    ON c.ref_id=e.chore_collection_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'BigPlan' as entity_tag,
        e.ref_id as ref_id,
        e.name as name,
        e.archived AS archived
    FROM big_plan_collection AS c
    JOIN big_plan AS e
    ON c.ref_id=e.big_plan_collection_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'Project' as entity_tag,
        e.ref_id as ref_id,
        e.name as name,
        e.archived AS archived
    FROM project_collection AS c
    JOIN project AS e
    ON c.ref_id=e.project_collection_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'Vacation' as entity_tag,
        e.ref_id as ref_id,
        e.name as name,
        e.archived AS archived
    FROM vacation_collection AS c
    JOIN vacation AS e
    ON c.ref_id=e.vacation_collection_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'SmartList' as entity_tag,
        e.ref_id as ref_id,
        e.name as name,
        e.archived AS archived
    FROM smart_list_collection AS c
    JOIN smart_list AS e
    ON c.ref_id=e.smart_list_collection_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'SmartListTag' as entity_tag,
        e.ref_id as ref_id,
        e.tag_name as name,
        e.archived AS archived
    FROM smart_list_collection AS c
    JOIN smart_list AS b
    ON c.ref_id=b.smart_list_collection_ref_id
    JOIN smart_list_tag as e
    ON b.ref_id=e.smart_list_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'SmartListItem' as entity_tag,
        e.ref_id as ref_id,
        e.name as name,
        e.archived AS archived
    FROM smart_list_collection AS c
    JOIN smart_list AS b
    ON c.ref_id=b.smart_list_collection_ref_id
    JOIN smart_list_item as e
    ON b.ref_id=e.smart_list_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'Metric' as entity_tag,
        e.ref_id as ref_id,
        e.name as name,
        e.archived AS archived
    FROM metric_collection AS c
    JOIN metric AS e
    ON c.ref_id=e.metric_collection_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'MetricEntry' as entity_tag,
        e.ref_id as ref_id,
        'Entry for ' || e.collection_time || ' value=' || e.value || ' notes=' || e.notes as name,
        e.archived AS archived
    FROM metric_collection AS c
    JOIN metric AS b
    ON c.ref_id=b.metric_collection_ref_id
    JOIN metric_entry as e
    ON b.ref_id=e.metric_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'Person' as entity_tag,
        e.ref_id as ref_id,
        e.name as name,
        e.archived AS archived
    FROM person_collection AS c
    JOIN person AS e
    ON c.ref_id=e.person_collection_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'SlackTask' as entity_tag,
        e.ref_id as ref_id,
        'Respond to ' || e.user || ' on channel ' || e.channel as name,
        e.archived AS archived
    FROM push_integration_group AS c
    JOIN slack_task_collection AS t
    ON c.ref_id = t.push_integration_group_ref_id
    JOIN slack_task AS e
    ON t.ref_id=e.slack_task_collection_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'EmailTask' as entity_tag,
        e.ref_id as ref_id,
        'Respond to message from ' || e.from_name || ' <' || e.from_address || '> about ' || e.subject as name,
        e.archived AS archived
    FROM push_integration_group AS c
    JOIN email_task_collection AS t
    ON c.ref_id = t.push_integration_group_ref_id
    JOIN email_task AS e
    ON t.ref_id=e.email_task_collection_ref_id;
    """
    )


def downgrade() -> None:
    op.execute("""drop table if exists search_index""")
