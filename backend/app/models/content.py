import uuid
from datetime import datetime, timezone
import sqlalchemy
from sqlalchemy import String, DateTime, Boolean, Enum as SA_ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


class LearningContent(Base):
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    content_type: Mapped[str] = mapped_column(SA_ENUM("COURSE", "ARTICLE", "VIDEO", "BOOK", name="content_type_enum", create_type=False))
    url: Mapped[str] = mapped_column(String(500), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=True)
    tags: Mapped[str] = mapped_column(String(500), nullable=True)  # JSON string of tags
    difficulty_level: Mapped[str] = mapped_column(String(20), nullable=True, default="BEGINNER")  # BEGINNER, INTERMEDIATE, ADVANCED
    estimated_minutes: Mapped[int] = mapped_column(sqlalchemy.Integer, nullable=True)
    embedding: Mapped[str] = mapped_column(sqlalchemy.Text, nullable=True)  # JSON serialized embedding vector
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    @property
    def difficulty(self) -> str | None:
        return self.difficulty_level

    # Relationships
    recommendations: Mapped[list["Recommendations"]] = relationship("Recommendations", back_populates="content")
    interactions: Mapped[list["UserContentInteraction"]] = relationship("UserContentInteraction", back_populates="content")


class Recommendations(Base):
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id: Mapped[str] = mapped_column(String(36), sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"), index=True)
    content_id: Mapped[str] = mapped_column(String(36), sqlalchemy.ForeignKey("learning_content.id", ondelete="CASCADE"), index=True)
    reason: Mapped[str] = mapped_column(String(500), nullable=True)
    score: Mapped[float] = mapped_column(sqlalchemy.Float, nullable=True, default=0.0)
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user: Mapped["Users"] = relationship("Users", back_populates="recommendations")
    content: Mapped["LearningContent"] = relationship("LearningContent", back_populates="recommendations")


class UserContentInteraction(Base):
    __tablename__ = "user_content_interactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id: Mapped[str] = mapped_column(String(36), sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"), index=True)
    content_id: Mapped[str] = mapped_column(String(36), sqlalchemy.ForeignKey("learning_content.id", ondelete="CASCADE"), index=True)
    interaction_type: Mapped[str] = mapped_column(String(20), nullable=False)  # view, like, complete, bookmark
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user: Mapped["Users"] = relationship("Users", back_populates="content_interactions")
    content: Mapped["LearningContent"] = relationship("LearningContent", back_populates="interactions")
