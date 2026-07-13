import uuid
from datetime import datetime, timezone
import sqlalchemy
from sqlalchemy import String, Boolean, DateTime, Enum as SA_ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class Challenges(Base):
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=True)
    duration_days: Mapped[int] = mapped_column(sqlalchemy.Integer, default=7)
    points_reward: Mapped[int] = mapped_column(sqlalchemy.Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user_challenges: Mapped[list["UserChallenges"]] = relationship("UserChallenges", back_populates="challenge")

class UserChallenges(Base):
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id: Mapped[str] = mapped_column(String(36), sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"), index=True)
    challenge_id: Mapped[str] = mapped_column(String(36), sqlalchemy.ForeignKey("challenges.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(SA_ENUM("ACTIVE", "COMPLETED", "FAILED", name="challenge_status_enum", create_type=False), default="ACTIVE")
    progress_days: Mapped[int] = mapped_column(sqlalchemy.Integer, default=0)
    last_checkin: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["Users"] = relationship("Users", back_populates="user_challenges")
    challenge: Mapped["Challenges"] = relationship("Challenges", back_populates="user_challenges")

class Achievements(Base):
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id: Mapped[str] = mapped_column(String(36), sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    icon: Mapped[str] = mapped_column(String(50), nullable=True)
    earned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user: Mapped["Users"] = relationship("Users", back_populates="achievements")
