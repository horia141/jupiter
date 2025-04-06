"""No more default difficulty

Revision ID: 33652d4a4b41
Revises: 9418c38d5709
Create Date: 2025-02-01 17:37:18.805113

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "33652d4a4b41"
down_revision = "9418c38d5709"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE inbox_task SET difficulty = 'easy' WHERE difficulty IS NULL;
        """
    )
    op.execute(
        """
            UPDATE habit
            SET gen_params = json_set(
                COALESCE(gen_params, '{}'), 
                '$.difficulty', 'easy'
            )
            WHERE json_extract(gen_params, '$.difficulty') IS NULL;
        """
    )
    op.execute(
        """
            UPDATE chore
            SET gen_params = json_set(
                COALESCE(gen_params, '{}'), 
                '$.difficulty', 'easy'
            )
            WHERE json_extract(gen_params, '$.difficulty') IS NULL;
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
                '$.difficulty', 'easy'
            )
            WHERE catch_up_params IS NOT NULL 
            AND json_extract(catch_up_params, '$.difficulty') IS NULL;
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
                '$.difficulty', 'easy'
            )
            WHERE collection_params IS NOT NULL 
            AND json_extract(collection_params, '$.difficulty') IS NULL;
        """
    )


def downgrade() -> None:
    pass
