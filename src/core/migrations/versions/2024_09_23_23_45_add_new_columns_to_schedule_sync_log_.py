"""Add new columns to schedule_sync_log_entry

Revision ID: 9232b5ece952
Revises: 5fd8a6a670e4
Create Date: 2024-09-23 23:45:36.050999

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9232b5ece952"
down_revision = "5fd8a6a670e4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("schedule_external_sync_log_entry") as batch_op:
        batch_op.add_column(sa.Column("today", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("start_of_window", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("end_of_window", sa.Date(), nullable=True))
        batch_op.add_column(
            sa.Column("sync_even_if_not_modified", sa.Boolean(), nullable=True)
        )

    op.execute(
        """
        UPDATE schedule_external_sync_log_entry
        SET today = date(created_time)
        WHERE today IS NULL;
    """
    )
    op.execute(
        """
        UPDATE schedule_external_sync_log_entry
        SET start_of_window = '2001-01-01'
        WHERE start_of_window IS NULL;
    """
    )
    op.execute(
        """
        UPDATE schedule_external_sync_log_entry
        SET end_of_window = '2050-12-31'
        WHERE end_of_window IS NULL;
    """
    )
    op.execute(
        """
        UPDATE schedule_external_sync_log_entry
        SET sync_even_if_not_modified = even_more_entity_records
        WHERE sync_even_if_not_modified IS NULL;
    """
    )


def downgrade():
    pass
