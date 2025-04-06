"""Add journals skip_rule

Revision ID: 5c4e136dcace
Revises: 66e1a41d5021
Create Date: 2025-02-09 10:18:50.524483

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "5c4e136dcace"
down_revision = "66e1a41d5021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE journal_collection
        SET writing_task_gen_params = json_set(
            COALESCE(writing_task_gen_params, '{}'), 
            '$.skip_rule', null
        )
        WHERE writing_task_gen_params IS NOT NULL;
    """
    )


def downgrade():
    pass
