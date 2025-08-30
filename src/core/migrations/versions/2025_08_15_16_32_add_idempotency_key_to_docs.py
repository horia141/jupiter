"""Add idempotency key to docs

Revision ID: 7d744f5e0d53
Revises: d4976405150e
Create Date: 2025-08-15 16:32:59.781759

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7d744f5e0d53"
down_revision = "d4976405150e"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("doc") as batch_op:
        batch_op.add_column(
            sa.Column("idempotency_key", sa.String(length=36), nullable=True)
        )

    op.execute(
        "UPDATE doc SET idempotency_key = 'key-' || ref_id WHERE idempotency_key IS NULL"
    )

    op.execute("CREATE UNIQUE INDEX idx_doc_idempotency_key ON doc (idempotency_key)")


def downgrade():
    pass
