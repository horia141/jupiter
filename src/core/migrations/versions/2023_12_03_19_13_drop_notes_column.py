"""Drop notes column

Revision ID: 4bbe968a2544
Revises: df4539fa3e07
Create Date: 2023-12-03 19:13:35.500054

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "4bbe968a2544"
down_revision = "df4539fa3e07"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the 'notes' column from the 'metric_entry' table
    with op.batch_alter_table("metric_entry") as batch_op:
        batch_op.drop_column("notes")


def downgrade() -> None:
    pass
