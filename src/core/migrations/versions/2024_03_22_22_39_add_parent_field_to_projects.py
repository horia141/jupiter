"""Add parent field to projects

Revision ID: af65a31f2252
Revises: 626b770f8db6
Create Date: 2024-03-22 22:39:50.982665

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "af65a31f2252"
down_revision = "626b770f8db6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    naming_convention = {
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
    with op.batch_alter_table(
        "project", naming_convention=naming_convention
    ) as batch_op:
        batch_op.add_column(
            sa.Column("parent_project_ref_id", sa.Integer, nullable=True)
        )
        batch_op.create_foreign_key(
            "fk_project_parent_project_ref_id_project",
            "project",
            ["parent_project_ref_id"],
            ["ref_id"],
        )
    op.execute(
        """
        CREATE INDEX ix_project_parent_project_ref_id ON project (parent_project_ref_id) WHERE parent_project_ref_id IS NOT NULL;"""
    )


def downgrade() -> None:
    pass
