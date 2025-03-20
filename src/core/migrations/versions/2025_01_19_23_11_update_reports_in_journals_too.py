"""Update reports in journals too

Revision ID: 99c845816b0b
Revises: 1930a77198c2
Create Date: 2025-01-19 23:11:12.945338

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "99c845816b0b"
down_revision = "1930a77198c2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE journal
        SET report = REPLACE(report, '"accepted_cnt"', '"not_started_cnt"')
        """
    )
    op.execute(
        """
        UPDATE journal
        SET report = REPLACE(report, '"accepted"', '"not_started"')
        """
    )


def downgrade() -> None:
    pass
