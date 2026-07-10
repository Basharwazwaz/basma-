"""Add AI ML tables and content enhancements

Revision ID: 0006
Revises: 0005
Create Date: 2026-07-10 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to learning_content
    op.add_column('learning_content', sa.Column('tags', sa.String(length=500), nullable=True))
    op.add_column('learning_content', sa.Column('difficulty_level', sa.String(length=20), nullable=True))
    op.add_column('learning_content', sa.Column('embedding', sa.Text(), nullable=True))

    # Add score column to recommendations
    op.add_column('recommendations', sa.Column('score', sa.Float(), nullable=True))

    # Create user_content_interactions table
    op.create_table('user_content_interactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interaction_type', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['content_id'], ['learning_content.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_content_interactions_id'), 'user_content_interactions', ['id'], unique=False)
    op.create_index(op.f('ix_user_content_interactions_user_id'), 'user_content_interactions', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_content_interactions_content_id'), 'user_content_interactions', ['content_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_content_interactions_content_id'), table_name='user_content_interactions')
    op.drop_index(op.f('ix_user_content_interactions_user_id'), table_name='user_content_interactions')
    op.drop_index(op.f('ix_user_content_interactions_id'), table_name='user_content_interactions')
    op.drop_table('user_content_interactions')

    op.drop_column('recommendations', 'score')
    op.drop_column('learning_content', 'embedding')
    op.drop_column('learning_content', 'difficulty_level')
    op.drop_column('learning_content', 'tags')
