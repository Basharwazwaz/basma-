import uuid
from datetime import datetime, timezone, date
import sqlalchemy
from sqlalchemy import String, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class WeeklyReports(Base):
    __tablename__ = "weekly_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"), index=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    metrics_summary: Mapped[dict] = mapped_column(JSONB, nullable=True) # E.g., total_screen_time, avg_mood
    ai_summary: Mapped[str] = mapped_column(String(2000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user: Mapped["Users"] = relationship("Users", back_populates="weekly_reports")

    __table_args__ = (
        sqlalchemy.Index("ix_weekly_reports_user_date", "user_id", "start_date", "end_date"),
    )

class AIInsights(Base):
    __tablename__ = "ai_insights"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"), index=True)
    insight_type: Mapped[str] = mapped_column(String(50), nullable=False) # E.g., WARNING, PRAISE, TIP
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    context_data: Mapped[dict] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user: Mapped["Users"] = relationship("Users", back_populates="ai_insights")

    __table_args__ = (
        sqlalchemy.Index("ix_ai_insights_user_type", "user_id", "insight_type"),
    )
