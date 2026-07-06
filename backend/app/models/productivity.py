import uuid
from datetime import datetime, date, time
import sqlalchemy
from sqlalchemy import String, Boolean, Date, DateTime, Time
from sqlalchemy.dialects.postgresql import UUID, ENUM as PG_ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class GoalStatusEnum(str, PG_ENUM):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"

class TaskStatusEnum(str, PG_ENUM):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

class Goals(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=True) # e.g. Education, Health
    status: Mapped[str] = mapped_column(PG_ENUM("NOT_STARTED", "IN_PROGRESS", "COMPLETED", "ABANDONED", name="goal_status_enum", create_type=False), default="NOT_STARTED")
    target_date: Mapped[date] = mapped_column(Date, nullable=True)
    progress_percent: Mapped[int] = mapped_column(sqlalchemy.Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["Users"] = relationship("Users", back_populates="goals")
    tasks: Mapped[list["Tasks"]] = relationship("Tasks", back_populates="goal", cascade="all, delete-orphan")

class Tasks(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"), index=True)
    goal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), sqlalchemy.ForeignKey("goals.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(PG_ENUM("PENDING", "IN_PROGRESS", "DONE", name="task_status_enum", create_type=False), default="PENDING")
    due_date: Mapped[date] = mapped_column(Date, nullable=True)
    pomodoro_sessions: Mapped[int] = mapped_column(sqlalchemy.Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["Users"] = relationship("Users", back_populates="tasks")
    goal: Mapped["Goals"] = relationship("Goals", back_populates="tasks")

class Planner(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    plan_date: Mapped[date] = mapped_column(Date, index=True)
    start_time: Mapped[time] = mapped_column(Time, nullable=True)
    end_time: Mapped[time] = mapped_column(Time, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    user: Mapped["Users"] = relationship("Users", back_populates="planner")
