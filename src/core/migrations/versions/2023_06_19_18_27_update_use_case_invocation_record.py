"""Update use case invocation record

Revision ID: fee96a64dd68
Revises: c7662aa06439
Create Date: 2023-06-19 18:27:30.320166

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "fee96a64dd68"
down_revision = "c7662aa06439"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("use_case_mutation_use_case_invocation_record")
    op.execute(
        """
CREATE TABLE use_case_mutation_use_case_invocation_record (
    user_ref_id INTEGER NOT NULL,
    workspace_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    name VARCHAR NOT NULL, 
    args JSON NOT NULL, 
    result VARCHAR NOT NULL, 
    error_str VARCHAR, 
    PRIMARY KEY (user_ref_id, workspace_ref_id, timestamp, name),
    FOREIGN KEY (user_ref_id) REFERENCES user (ref_id),
    FOREIGN KEY (workspace_ref_id) REFERENCES workspace (ref_id)
);"""
    )


def downgrade():
    pass
