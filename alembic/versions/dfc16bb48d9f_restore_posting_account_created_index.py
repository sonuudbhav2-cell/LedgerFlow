"""restore_posting_account_created_index

Revision ID: dfc16bb48d9f
Revises: f2c0064de257
Create Date: 2026-08-29 16:44:32.305118

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'dfc16bb48d9f'
down_revision = 'f2c0064de257'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        'ix_postings_account_direction',
        'postings',
        ['account_id', 'direction'],
        unique=False,
        if_not_exists=True
    )


def downgrade() -> None:
    op.drop_index('ix_postings_account_direction', table_name='postings', if_exists=True)