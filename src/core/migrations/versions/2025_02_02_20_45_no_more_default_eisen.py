"""No more default eisen

Revision ID: c3b952bcd8c2
Revises: 33652d4a4b41
Create Date: 2025-02-02 20:45:44.563427

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "c3b952bcd8c2"
down_revision = "33652d4a4b41"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE inbox_task SET eisen = 'regular' WHERE eisen IS NULL;
        """
    )
    op.execute(
        """
            UPDATE habit
            SET gen_params = json_set(
                COALESCE(gen_params, '{}'), 
                '$.eisen', 'regular'
            )
            WHERE json_extract(gen_params, '$.eisen') IS NULL;
        """
    )
    op.execute(
        """
            UPDATE chore
            SET gen_params = json_set(
                COALESCE(gen_params, '{}'), 
                '$.eisen', 'regular'
            )
            WHERE json_extract(gen_params, '$.eisen') IS NULL;
        """
    )
    op.execute(
        """UPDATE person SET catch_up_params = null WHERE catch_up_params='null';"""
    )
    op.execute(
        """
            UPDATE person
            SET catch_up_params = json_set(
                COALESCE(catch_up_params, '{}'), 
                '$.eisen', 'regular'
            )
            WHERE catch_up_params IS NOT NULL 
            AND json_extract(catch_up_params, '$.eisen') IS NULL;
        """
    )
    op.execute(
        """UPDATE metric SET collection_params = null WHERE collection_params='null';"""
    )
    op.execute(
        """
            UPDATE metric
            SET collection_params = json_set(
                COALESCE(collection_params, '{}'), 
                '$.eisen', 'regular'
            )
            WHERE collection_params IS NOT NULL 
            AND json_extract(collection_params, '$.eisen') IS NULL;
        """
    )


def downgrade() -> None:
    pass
