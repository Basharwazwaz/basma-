"""Add profile settings columns + gender + interests

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-05 19:30:00.000000

Changes:
  - profiles.gender              VARCHAR(20) NULL
  - profiles.interests           TEXT[]      NULL  DEFAULT '{}'
  - profiles.language            VARCHAR(5)  NOT NULL DEFAULT 'ar'
  - profiles.theme               VARCHAR(10) NOT NULL DEFAULT 'light'
  - profiles.notifications_enabled BOOLEAN   NOT NULL DEFAULT TRUE
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # gender — was missing from the initial migration
    op.add_column(
        'profiles',
        sa.Column('gender', sa.String(length=20), nullable=True)
    )

    # interests — native PostgreSQL TEXT[] array
    op.add_column(
        'profiles',
        sa.Column(
            'interests',
            postgresql.ARRAY(sa.Text()),
            nullable=True,
            server_default='{}',
        )
    )

    # language — UI language preference ('ar' | 'en')
    op.add_column(
        'profiles',
        sa.Column(
            'language',
            sa.String(length=5),
            nullable=False,
            server_default='ar',
        )
    )

    # theme — UI theme ('light' | 'dark')
    op.add_column(
        'profiles',
        sa.Column(
            'theme',
            sa.String(length=10),
            nullable=False,
            server_default='light',
        )
    )

    # notifications_enabled — push/in-app notification toggle
    op.add_column(
        'profiles',
        sa.Column(
            'notifications_enabled',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('TRUE'),
        )
    )


def downgrade() -> None:
    op.drop_column('profiles', 'notifications_enabled')
    op.drop_column('profiles', 'theme')
    op.drop_column('profiles', 'language')
    op.drop_column('profiles', 'interests')
    op.drop_column('profiles', 'gender')
