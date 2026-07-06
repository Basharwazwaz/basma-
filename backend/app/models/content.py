import uuid
from datetime import datetime
import sqlalchemy
from sqlalchemy import String, DateTime
from sqlalchemy.dialects.postgresql import UUID, ENUM as PG_ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class ContentTypeEnum(str, PG_ENUM):
    COURSE = "COURSE"
    ARTICLE = "ARTICLE"
    VIDEO = "VIDEO"
    BOOK = "BOOK"

class LearningContent(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    content_type: Mapped[str] = mapped_column(PG_ENUM("COURSE", "ARTICLE", "VIDEO", "BOOK", name="content_type_enum", create_type=False))
    url: Mapped[str] = mapped_column(String(500), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=True)
    estimated_minutes: Mapped[int] = mapped_column(sqlalchemy.Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    recommendations: Mapped[list["Recommendations"]] = relationship("Recommendations", back_populates="content")

class Recommendations(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"), index=True)
    content_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), sqlalchemy.ForeignKey("learning_content.id", ondelete="CASCADE"), index=True)
    reason: Mapped[str] = mapped_column(String(500), nullable=True)
    is_dismissed: Mapped[bool] = mapped_column(sqlalchemy.Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    user: Mapped["Users"] = relationship("Users", back_populates="recommendations")
    content: Mapped["LearningContent"] = relationship("LearningContent", back_populates="recommendations")
