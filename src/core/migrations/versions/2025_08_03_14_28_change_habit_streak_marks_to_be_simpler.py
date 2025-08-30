"""Change habit_streak_marks to be simpler

Revision ID: d4976405150e
Revises: 846fedf15dd7
Create Date: 2025-08-03 14:28:39.684855

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "d4976405150e"
down_revision = "846fedf15dd7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("habit_streak_marks") as batch_op:
        batch_op.drop_column("year")


def downgrade() -> None:
    pass
