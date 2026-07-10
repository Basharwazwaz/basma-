import uuid
import sqlalchemy
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import String, Boolean, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, ENUM as PG_ENUM, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Users(Base):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        PG_ENUM("ADMIN", "USER", name="role_enum", create_type=False), default="USER"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    profile: Mapped["Profiles"] = relationship(
        "Profiles", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    moods: Mapped[list["Mood"]] = relationship(
        "Mood", back_populates="user", cascade="all, delete-orphan"
    )
    digital_habits: Mapped[list["DigitalHabits"]] = relationship(
        "DigitalHabits", back_populates="user", cascade="all, delete-orphan"
    )
    goals: Mapped[list["Goals"]] = relationship(
        "Goals", back_populates="user", cascade="all, delete-orphan"
    )
    tasks: Mapped[list["Tasks"]] = relationship(
        "Tasks", back_populates="user", cascade="all, delete-orphan"
    )
    planner: Mapped[list["Planner"]] = relationship(
        "Planner", back_populates="user", cascade="all, delete-orphan"
    )
    user_challenges: Mapped[list["UserChallenges"]] = relationship(
        "UserChallenges", back_populates="user", cascade="all, delete-orphan"
    )
    achievements: Mapped[list["Achievements"]] = relationship(
        "Achievements", back_populates="user", cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["Recommendations"]] = relationship(
        "Recommendations", back_populates="user", cascade="all, delete-orphan"
    )
    notifications: Mapped[list["Notifications"]] = relationship(
        "Notifications", back_populates="user", cascade="all, delete-orphan"
    )
    weekly_reports: Mapped[list["WeeklyReports"]] = relationship(
        "WeeklyReports", back_populates="user", cascade="all, delete-orphan"
    )
    ai_insights: Mapped[list["AIInsights"]] = relationship(
        "AIInsights", back_populates="user", cascade="all, delete-orphan"
    )
    refresh_tokens: Mapped[list["RefreshTokens"]] = relationship(
        "RefreshTokens", back_populates="user", cascade="all, delete-orphan"
    )
    coach_messages: Mapped[list["CoachMessages"]] = relationship(
        "CoachMessages", back_populates="user", cascade="all, delete-orphan"
    )
    content_interactions: Mapped[list["UserContentInteraction"]] = relationship(
        "UserContentInteraction", back_populates="user", cascade="all, delete-orphan"
    )


class Profiles(Base):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )

    # ── Personal Info ──────────────────────────────────────────────────────
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    # Consistent with Phase 2: stored as 'major' (represents field of study / education)
    major: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    # ── Digital Behaviour Targets ──────────────────────────────────────────
    target_screen_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)   # minutes/day
    target_sleep_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)    # minutes/night

    # ── Gamification ───────────────────────────────────────────────────────
    points: Mapped[int] = mapped_column(Integer, default=0)

    # ── Interests (Phase 4) ─────────────────────────────────────────────────
    # Stored as a native PostgreSQL TEXT[] array — no join table needed
    interests: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(Text), nullable=True, default=list
    )

    # ── Settings (Phase 4) ──────────────────────────────────────────────────
    language: Mapped[str] = mapped_column(String(5), nullable=False, default="ar")
    theme: Mapped[str] = mapped_column(String(10), nullable=False, default="light")
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # ── Timestamps ──────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationship
    user: Mapped["Users"] = relationship("Users", back_populates="profile")
