"""Backfill schedule data

Revision ID: 771083f238d7
Revises: 45fe25fb545d
Create Date: 2024-07-07 19:07:19.904483

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "771083f238d7"
down_revision = "45fe25fb545d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO schedule_domain
               SELECT
                   ref_id as ref_id,
                   1 as version,
                   0 as archived,
                   created_time as created_time,
                   created_time as last_modified_time,
                   null as archived_time,
                   ref_id as workspace_ref_id
               FROM workspace;
        """
    )
    op.execute(
        """
        INSERT INTO schedule_domain_event
                SELECT
                    ref_id as owner_ref_id,
                    created_time as timestamp,
                    0 as session_index,
                    'Created' as name,
                    'CLI' as source,
                    1 as owner_version,
                    'Created' as kind,
                    '{}}' as data
                FROM workspace;
        """
    )
    op.execute(
        """
        UPDATE workspace
        SET feature_flags = json_set(feature_flags, '$.schedule', 'true')
        """
    )
    op.execute(
        """
        INSERT INTO schedule_stream
        SELECT ref_id as ref_id,
               1 as version,
               0 as archived,
               created_time as created_time,
               created_time as last_modified_time,
               null as archived_time,
               ref_id as schedule_domain_ref_id,
               'user' as source,
               'Events' as name,
               'blue' as color,
               null as source_ical_url
        FROM schedule_domain;
    """
    )
    op.execute(
        """
        INSERT INTO schedule_stream_event
        SELECT ref_id as owner_ref_id,
               created_time as timestamp,
               0 as session_index,
               'Created' as name,
               'CLI' as source,
               1 as owner_version,
               'Created' as kind,
               '{}' as data
        FROM schedule_domain;
    """
    )


def downgrade() -> None:
    pass
