"""Add column for more log entries

Revision ID: 5bd25a8a7c69
Revises: fbf223b452c4
Create Date: 2024-09-20 09:52:44.913176

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5bd25a8a7c69"
down_revision = "fbf223b452c4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("schedule_external_sync_log_entry") as batch_op:
        batch_op.add_column(
            sa.Column("even_more_entity_records", sa.Boolean(), nullable=True)
        )

    op.execute(
        """
        UPDATE schedule_external_sync_log_entry
        SET even_more_entity_records = FALSE
        WHERE even_more_entity_records IS NULL;
    """
    )


def downgrade() -> None:
    pass
