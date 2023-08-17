"""Add user feature_flags column

Revision ID: a8268d01e4c1
Revises: fbdcd37bbdae
Create Date: 2023-08-17 21:48:03.920299

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a8268d01e4c1"
down_revision = "fbdcd37bbdae"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user") as batch_op:
        batch_op.add_column(sa.Column("feature_flags", sa.JSON))
    op.execute("""update user set feature_flags='{"gamification-scores": true}'""")
    with op.batch_alter_table("user") as batch_op:
        batch_op.alter_column("feature_flags", existing_type=sa.JSON, nullable=False)


def downgrade():
    pass
