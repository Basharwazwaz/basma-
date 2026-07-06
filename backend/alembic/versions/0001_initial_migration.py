"""Initial migration

Revision ID: 0001
Revises: 
Create Date: 2026-07-05 19:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # --- Enums ---
    op.execute("CREATE TYPE role_enum AS ENUM ('ADMIN', 'USER')")
    op.execute("CREATE TYPE mood_enum AS ENUM ('EXCELLENT', 'GOOD', 'NEUTRAL', 'BAD', 'TERRIBLE')")
    op.execute("CREATE TYPE goal_status_enum AS ENUM ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'ABANDONED')")
    op.execute("CREATE TYPE task_status_enum AS ENUM ('PENDING', 'IN_PROGRESS', 'DONE')")
    op.execute("CREATE TYPE challenge_status_enum AS ENUM ('ACTIVE', 'COMPLETED', 'FAILED')")
    op.execute("CREATE TYPE content_type_enum AS ENUM ('COURSE', 'ARTICLE', 'VIDEO', 'BOOK')")

    # --- Users ---
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', postgresql.ENUM('ADMIN', 'USER', name='role_enum', create_type=False), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # --- Profiles ---
    op.create_table('profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('major', sa.String(length=150), nullable=True),
        sa.Column('target_screen_time', sa.Integer(), nullable=True),
        sa.Column('target_sleep_time', sa.Integer(), nullable=True),
        sa.Column('points', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_profiles_id'), 'profiles', ['id'], unique=False)

    # --- Mood ---
    op.create_table('mood',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('record_date', sa.Date(), nullable=False),
        sa.Column('mood_score', sa.Integer(), nullable=False),
        sa.Column('stress_score', sa.Integer(), nullable=False),
        sa.Column('mood_state', postgresql.ENUM('EXCELLENT', 'GOOD', 'NEUTRAL', 'BAD', 'TERRIBLE', name='mood_enum', create_type=False), nullable=False),
        sa.Column('note', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'record_date', name='uix_user_record_date_mood')
    )
    op.create_index(op.f('ix_mood_id'), 'mood', ['id'], unique=False)
    op.create_index(op.f('ix_mood_record_date'), 'mood', ['record_date'], unique=False)

    # --- Digital Habits ---
    op.create_table('digital_habits',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('record_date', sa.Date(), nullable=False),
        sa.Column('screen_time_minutes', sa.Integer(), nullable=False),
        sa.Column('social_media_minutes', sa.Integer(), nullable=False),
        sa.Column('sleep_minutes', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'record_date', name='uix_user_record_date_habits')
    )
    op.create_index(op.f('ix_digital_habits_id'), 'digital_habits', ['id'], unique=False)
    op.create_index(op.f('ix_digital_habits_record_date'), 'digital_habits', ['record_date'], unique=False)

    # --- Goals ---
    op.create_table('goals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('status', postgresql.ENUM('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'ABANDONED', name='goal_status_enum', create_type=False), nullable=False),
        sa.Column('target_date', sa.Date(), nullable=True),
        sa.Column('progress_percent', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_goals_id'), 'goals', ['id'], unique=False)

    # --- Tasks ---
    op.create_table('tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('goal_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('is_completed', sa.Boolean(), nullable=False),
        sa.Column('status', postgresql.ENUM('PENDING', 'IN_PROGRESS', 'DONE', name='task_status_enum', create_type=False), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('pomodoro_sessions', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_tasks_id'), 'tasks', ['id'], unique=False)

    # --- Planner ---
    op.create_table('planner',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('plan_date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=True),
        sa.Column('end_time', sa.Time(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_planner_id'), 'planner', ['id'], unique=False)
    op.create_index(op.f('ix_planner_plan_date'), 'planner', ['plan_date'], unique=False)

    # --- Challenges ---
    op.create_table('challenges',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('duration_days', sa.Integer(), nullable=False),
        sa.Column('points_reward', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index(op.f('ix_challenges_id'), 'challenges', ['id'], unique=False)

    # --- User Challenges ---
    op.create_table('user_challenges',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('challenge_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', postgresql.ENUM('ACTIVE', 'COMPLETED', 'FAILED', name='challenge_status_enum', create_type=False), nullable=False),
        sa.Column('progress_days', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_user_challenges_id'), 'user_challenges', ['id'], unique=False)

    # --- Achievements ---
    op.create_table('achievements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('earned_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_achievements_id'), 'achievements', ['id'], unique=False)

    # --- Learning Content ---
    op.create_table('learning_content',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('content_type', postgresql.ENUM('COURSE', 'ARTICLE', 'VIDEO', 'BOOK', name='content_type_enum', create_type=False), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('estimated_minutes', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index(op.f('ix_learning_content_id'), 'learning_content', ['id'], unique=False)

    # --- Recommendations ---
    op.create_table('recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.Column('is_dismissed', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['content_id'], ['learning_content.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_recommendations_id'), 'recommendations', ['id'], unique=False)

    # --- Weekly Reports ---
    op.create_table('weekly_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('metrics_summary', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ai_summary', sa.String(length=2000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_weekly_reports_id'), 'weekly_reports', ['id'], unique=False)

    # --- AI Insights ---
    op.create_table('ai_insights',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('insight_type', sa.String(length=50), nullable=False),
        sa.Column('message', sa.String(length=1000), nullable=False),
        sa.Column('context_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_ai_insights_id'), 'ai_insights', ['id'], unique=False)

    # --- Notifications ---
    op.create_table('notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.String(length=1000), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False),
        sa.Column('action_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)


def downgrade() -> None:
    # Drop all tables
    op.drop_table('notifications')
    op.drop_table('ai_insights')
    op.drop_table('weekly_reports')
    op.drop_table('recommendations')
    op.drop_table('learning_content')
    op.drop_table('achievements')
    op.drop_table('user_challenges')
    op.drop_table('challenges')
    op.drop_table('planner')
    op.drop_table('tasks')
    op.drop_table('goals')
    op.drop_table('digital_habits')
    op.drop_table('mood')
    op.drop_table('profiles')
    op.drop_table('users')

    # Drop enums
    op.execute("DROP TYPE content_type_enum")
    op.execute("DROP TYPE challenge_status_enum")
    op.execute("DROP TYPE task_status_enum")
    op.execute("DROP TYPE goal_status_enum")
    op.execute("DROP TYPE mood_enum")
    op.execute("DROP TYPE role_enum")
