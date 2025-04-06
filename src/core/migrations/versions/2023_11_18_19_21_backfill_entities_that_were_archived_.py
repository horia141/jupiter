"""Backfill entities that were archived and modified

Revision ID: 9d154be8e4c1
Revises: 332900a57518
Create Date: 2023-11-18 19:21:03.310221

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "9d154be8e4c1"
down_revision = "332900a57518"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""DELETE FROM search_index""")
    op.execute(
        """
        UPDATE chore 
        SET archived_time=last_modified_time 
        WHERE archived=true AND archived_time IS null;"""
    )

    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'InboxTask' AS entity_tag,
        c.ref_id AS parent_ref_id,
        e.ref_id AS ref_id,
        e.name AS name,
        e.archived AS archived,
        e.created_time AS created_time,
        e.last_modified_time AS last_modified_time,
        e.archived_time AS archived_time
    FROM inbox_task_collection AS c
    JOIN inbox_task AS e
    ON c.ref_id=e.inbox_task_collection_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'Habit' AS entity_tag,
        c.ref_id AS parent_ref_id,
        e.ref_id AS ref_id,
        e.name AS name,
        e.archived AS archived,
        e.created_time AS created_time,
        e.last_modified_time AS last_modified_time,
        e.archived_time AS archived_time
    FROM habit_collection AS c
    JOIN habit AS e
    ON c.ref_id=e.habit_collection_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'Chore' AS entity_tag,
        c.ref_id AS parent_ref_id,
        e.ref_id AS ref_id,
        e.name AS name,
        e.archived AS archived,
        e.created_time AS created_time,
        e.last_modified_time AS last_modified_time,
        e.archived_time AS archived_time
    FROM chore_collection AS c
    JOIN chore AS e
    ON c.ref_id=e.chore_collection_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'BigPlan' AS entity_tag,
        c.ref_id AS parent_ref_id,
        e.ref_id AS ref_id,
        e.name AS name,
        e.archived AS archived,
        e.created_time AS created_time,
        e.last_modified_time AS last_modified_time,
        e.archived_time AS archived_time
    FROM big_plan_collection AS c
    JOIN big_plan AS e
    ON c.ref_id=e.big_plan_collection_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'Project' AS entity_tag,
        c.ref_id AS parent_ref_id,
        e.ref_id AS ref_id,
        e.name AS name,
        e.archived AS archived,
        e.created_time AS created_time,
        e.last_modified_time AS last_modified_time,
        e.archived_time AS archived_time
    FROM project_collection AS c
    JOIN project AS e
    ON c.ref_id=e.project_collection_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'Vacation' AS entity_tag,
        c.ref_id AS parent_ref_id,
        e.ref_id AS ref_id,
        e.name AS name,
        e.archived AS archived,
        e.created_time AS created_time,
        e.last_modified_time AS last_modified_time,
        e.archived_time AS archived_time
    FROM vacation_collection AS c
    JOIN vacation AS e
    ON c.ref_id=e.vacation_collection_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'SmartList' AS entity_tag,
        c.ref_id AS parent_ref_id,
        e.ref_id AS ref_id,
        e.name AS name,
        e.archived AS archived,
        e.created_time AS created_time,
        e.last_modified_time AS last_modified_time,
        e.archived_time AS archived_time
    FROM smart_list_collection AS c
    JOIN smart_list AS e
    ON c.ref_id=e.smart_list_collection_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'SmartListTag' AS entity_tag,
        b.ref_id AS parent_ref_id,
        e.ref_id AS ref_id,
        e.tag_name AS name,
        e.archived AS archived,
        e.created_time AS created_time,
        e.last_modified_time AS last_modified_time,
        e.archived_time AS archived_time
    FROM smart_list_collection AS c
    JOIN smart_list AS b
    ON c.ref_id=b.smart_list_collection_ref_id
    JOIN smart_list_tag AS e
    ON b.ref_id=e.smart_list_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'SmartListItem' AS entity_tag,
        b.ref_id AS parent_ref_id,
        e.ref_id AS ref_id,
        e.name AS name,
        e.archived AS archived,
        e.created_time AS created_time,
        e.last_modified_time AS last_modified_time,
        e.archived_time AS archived_time
    FROM smart_list_collection AS c
    JOIN smart_list AS b
    ON c.ref_id=b.smart_list_collection_ref_id
    JOIN smart_list_item AS e
    ON b.ref_id=e.smart_list_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'Metric' AS entity_tag,
        c.ref_id AS parent_ref_id,
        e.ref_id AS ref_id,
        e.name AS name,
        e.archived AS archived,
        e.created_time AS created_time,
        e.last_modified_time AS last_modified_time,
        e.archived_time AS archived_time
    FROM metric_collection AS c
    JOIN metric AS e
    ON c.ref_id=e.metric_collection_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'MetricEntry' AS entity_tag,
        b.ref_id AS parent_ref_id,
        e.ref_id AS ref_id,
        'Entry for ' || e.collection_time || ' value=' || e.value || ' notes=' || e.notes AS name,
        e.archived AS archived,
        e.created_time AS created_time,
        e.last_modified_time AS last_modified_time,
        e.archived_time AS archived_time
    FROM metric_collection AS c
    JOIN metric AS b
    ON c.ref_id=b.metric_collection_ref_id
    JOIN metric_entry AS e
    ON b.ref_id=e.metric_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'Person' AS entity_tag,
        c.ref_id AS parent_ref_id,
        e.ref_id AS ref_id,
        e.name AS name,
        e.archived AS archived,
        e.created_time AS created_time,
        e.last_modified_time AS last_modified_time,
        e.archived_time AS archived_time
    FROM person_collection AS c
    JOIN person AS e
    ON c.ref_id=e.person_collection_ref_id;
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'SlackTask' AS entity_tag,
        c.ref_id AS parent_ref_id,
        e.ref_id AS ref_id,
        'Respond to ' || e.user || ' on channel ' || e.channel AS name,
        e.archived AS archived,
        e.created_time AS created_time,
        e.last_modified_time AS last_modified_time,
        e.archived_time AS archived_time
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
        'EmailTask' AS entity_tag,
        c.ref_id AS parent_ref_id,
        e.ref_id AS ref_id,
        'Respond to message from ' || e.from_name || ' <' || e.from_address || '> about ' || e.subject AS name,
        e.archived AS archived,
        e.created_time AS created_time,
        e.last_modified_time AS last_modified_time,
        e.archived_time AS archived_time
    FROM push_integration_group AS c
    JOIN email_task_collection AS t
    ON c.ref_id = t.push_integration_group_ref_id
    JOIN email_task AS e
    ON t.ref_id=e.email_task_collection_ref_id;
    """
    )


def downgrade():
    pass
