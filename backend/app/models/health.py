import uuid
from datetime import datetime, timezone, date
import sqlalchemy
from sqlalchemy import String, Date, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, ENUM as PG_ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class Mood(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"), index=True)
    record_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date(), index=True)
    mood_score: Mapped[int] = mapped_column(sqlalchemy.Integer) # 1-10
    stress_score: Mapped[int] = mapped_column(sqlalchemy.Integer) # 1-10
    mood_state: Mapped[str] = mapped_column(PG_ENUM("EXCELLENT", "GOOD", "NEUTRAL", "BAD", "TERRIBLE", name="mood_enum", create_type=False))
    note: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user: Mapped["Users"] = relationship("Users", back_populates="moods")

    __table_args__ = (
        UniqueConstraint("user_id", "record_date", name="uix_user_record_date_mood"),
    )

class DigitalHabits(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"), index=True)
    record_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date(), index=True)
    screen_time_minutes: Mapped[int] = mapped_column(sqlalchemy.Integer, default=0)
    social_media_minutes: Mapped[int] = mapped_column(sqlalchemy.Integer, default=0)
    sleep_minutes: Mapped[int] = mapped_column(sqlalchemy.Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user: Mapped["Users"] = relationship("Users", back_populates="digital_habits")

    __table_args__ = (
        UniqueConstraint("user_id", "record_date", name="uix_user_record_date_habits"),
    )
