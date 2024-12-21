"""Fix some borked dataz

Revision ID: 760292ab1a52
Revises: b1cb91885cb2
Create Date: 2023-12-30 23:33:00.431744

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "760292ab1a52"
down_revision = "b1cb91885cb2"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
    update smart_list_item set tags_ref_id = '[]'
    where smart_list_ref_id = 15;
    """
    )


def downgrade():
    pass
