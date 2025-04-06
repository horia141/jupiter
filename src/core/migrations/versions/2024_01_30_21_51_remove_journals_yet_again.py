"""Remove journals yet again

Revision ID: dad9d96b473b
Revises: d074ebd1c713
Create Date: 2024-01-30 21:51:55.259415

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "dad9d96b473b"
down_revision = "d074ebd1c713"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""delete from journal;""")
    op.execute("""delete from note where domain='journal';""")


def downgrade() -> None:
    pass
