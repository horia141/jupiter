"""Add structures for habit streaks

Revision ID: cffeab8d94a2
Revises: e02518a0fcc7
Create Date: 2025-04-26 20:27:40.524188

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "cffeab8d94a2"
down_revision = "e02518a0fcc7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE habit_streak_marks (
            habit_ref_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            date DATE NOT NULL,
            statuses JSON NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            PRIMARY KEY (habit_ref_id, year, date),
            FOREIGN KEY (habit_ref_id) REFERENCES habit (ref_id)
        )
    """
    )


def downgrade() -> None:
    op.drop_table("habit_streak_marks")
