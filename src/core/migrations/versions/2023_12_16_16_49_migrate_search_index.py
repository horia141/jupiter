"""Migrate search index

Revision ID: d6e189bbdc0a
Revises: 8e317829bf1f
Create Date: 2023-12-16 16:49:26.926870

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "d6e189bbdc0a"
down_revision = "8e317829bf1f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
    UPDATE search_index
    SET entity_tag = 'Doc'
    WHERE entity_tag = 'Note';
    """
    )


def downgrade() -> None:
    pass
