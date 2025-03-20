"""Drop journals cause they broke

Revision ID: 4933a4869c5b
Revises: 75a742597704
Create Date: 2024-01-17 23:41:38.530621

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "4933a4869c5b"
down_revision = "75a742597704"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""delete from journal;""")
    op.execute("""delete from note where domain='journal';""")


def downgrade() -> None:
    pass
