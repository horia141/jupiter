"""Backfill skip rule in gen params

Revision ID: 8a9b3cca251c
Revises: 8ff19872296e
Create Date: 2025-02-07 23:06:31.296298

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "8a9b3cca251c"
down_revision = "8ff19872296e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE habit
        SET gen_params = json_set(
            COALESCE(gen_params, '{}'), 
            '$.skip_rule', skip_rule
        );
    """
    )
    op.execute(
        """
        UPDATE chore
        SET gen_params = json_set(
            COALESCE(gen_params, '{}'), 
            '$.skip_rule', skip_rule
        );
    """
    )
    op.execute(
        """
        UPDATE metric
        SET collection_params = json_set(
            COALESCE(collection_params, '{}'), 
            '$.skip_rule', null
        )
        WHERE collection_params IS NOT NULL;
    """
    )
    op.execute(
        """
        UPDATE person
        SET catch_up_params = json_set(
            COALESCE(catch_up_params, '{}'), 
            '$.skip_rule', null
        )
        WHERE catch_up_params IS NOT NULL;
    """
    )
    try:
        with op.batch_alter_table("habit") as batch_op:
            batch_op.drop_column("skip_rule")
    except KeyError:
        pass
    try:
        with op.batch_alter_table("chore") as batch_op:
            batch_op.drop_column("skip_rule")
    except KeyError:
        pass


def downgrade() -> None:
    pass
