"""Add coach messages

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-06 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('coach_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_coach_messages_id'), 'coach_messages', ['id'], unique=False)
    op.create_index(op.f('ix_coach_messages_user_id'), 'coach_messages', ['user_id'], unique=False)
    op.create_index(op.f('ix_coach_messages_created_at'), 'coach_messages', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_coach_messages_created_at'), table_name='coach_messages')
    op.drop_index(op.f('ix_coach_messages_user_id'), table_name='coach_messages')
    op.drop_index(op.f('ix_coach_messages_id'), table_name='coach_messages')
    op.drop_table('coach_messages')
