"""Add last_checkin to user_challenges

Revision ID: 0007
Revises: 0006
Create Date: 2026-07-10 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '0007'
down_revision = '0006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'user_challenges',
        sa.Column('last_checkin', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('user_challenges', 'last_checkin')
