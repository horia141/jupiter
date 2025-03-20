"""New structure for skip rules

Revision ID: 66e1a41d5021
Revises: 8a9b3cca251c
Create Date: 2025-02-08 15:12:11.905045

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "66e1a41d5021"
down_revision = "8a9b3cca251c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE habit
        SET gen_params =  json_set(
               gen_params, 
               '$.skip_rule',
               null
            )
        WHERE json_extract(gen_params, '$.skip_rule') IS NOT NULL
        AND json_extract(gen_params, '$.skip_rule') NOT IN ('"even"', '"odd"')
        AND json_valid(json_extract(gen_params, '$.skip_rule'))
        AND json_extract(gen_params, '$.skip_rule') LIKE '[%';
    """
    )
    op.execute(
        """
        UPDATE chore
        SET gen_params =  json_set(
               gen_params, 
               '$.skip_rule',
               null
            )
        WHERE json_extract(gen_params, '$.skip_rule') IS NOT NULL
        AND json_extract(gen_params, '$.skip_rule') NOT IN ('"even"', '"odd"')
        AND json_valid(json_extract(gen_params, '$.skip_rule'))
        AND json_extract(gen_params, '$.skip_rule') LIKE '[%';
    """
    )


def downgrade() -> None:
    pass
