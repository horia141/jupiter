"""Fix some issues with gc and gen logs

Revision ID: b1cb91885cb2
Revises: f2d273fd9af4
Create Date: 2023-12-23 18:22:51.831390

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "b1cb91885cb2"
down_revision = "f2d273fd9af4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        update gc_log_entry
        set gc_targets = '["inbox-tasks", "habits", "chores", "big-plans", "docs", "vacations", "projects", "smart-lists", "metrics", "persons"]';
    """
    )
    op.execute(
        """
        update gen_log_entry
        set gen_targets = '["inbox-tasks", "habits", "chores", "big-plans", "docs", "vacations", "projects", "smart-lists", "metrics", "persons"]';
    """
    )


def downgrade():
    pass
