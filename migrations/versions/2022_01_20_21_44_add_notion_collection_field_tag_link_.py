"""Add notion collection field tag link table

Revision ID: 06636bccb6f1
Revises: 3d59562f6736
Create Date: 2022-01-20 21:44:31.758837

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '06636bccb6f1'
down_revision = '3d59562f6736'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'notion_collection_field_tag_link',
        sa.Column('the_key', sa.String, primary_key=True),
        sa.Column('collection_key', sa.String, sa.ForeignKey('notion_collection_link.the_key'), index=True, nullable=False),
        sa.Column('field', sa.String, nullable=False),
        sa.Column('ref_id', sa.String, nullable=False),
        sa.Column('notion_id', sa.String, nullable=False),
        sa.Column('created_time', sa.DateTime, nullable=False),
        sa.Column('last_modified_time', sa.DateTime, nullable=False))


def downgrade() -> None:
    op.drop_table('notion_collection_field_tag_link')
