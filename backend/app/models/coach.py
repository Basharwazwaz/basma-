import uuid
from datetime import datetime, timezone
import sqlalchemy
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


class CoachMessages(Base):
    __tablename__ = "coach_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id: Mapped[str] = mapped_column(String(36), sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    user: Mapped["Users"] = relationship("Users", back_populates="coach_messages")

    __table_args__ = (
        sqlalchemy.Index("ix_coach_messages_user_created", "user_id", "created_at"),
    )
