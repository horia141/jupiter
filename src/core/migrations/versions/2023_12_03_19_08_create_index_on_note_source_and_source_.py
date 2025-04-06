"""Create index on note source and source entity

Revision ID: df4539fa3e07
Revises: 89d9d7551d95
Create Date: 2023-12-03 19:08:08.127661

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "df4539fa3e07"
down_revision = "89d9d7551d95"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
    CREATE UNIQUE INDEX ix_note_source_source_entity_ref_id ON note (source, source_entity_ref_id)
    WHERE source IS NOT 'user';
    """
    )


def downgrade() -> None:
    pass
