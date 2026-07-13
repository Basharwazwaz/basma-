from typing import Literal, Optional, List
from datetime import date, datetime, time
from pydantic import BaseModel, Field
# --- Goals ---

class GoalBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=50)
    status: Optional[Literal["NOT_STARTED", "IN_PROGRESS", "COMPLETED", "ABANDONED"]] = Field("NOT_STARTED")
    target_date: Optional[date] = None
    progress_percent: Optional[int] = Field(0, ge=0, le=100)

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=50)
    status: Optional[Literal["NOT_STARTED", "IN_PROGRESS", "COMPLETED", "ABANDONED"]] = None
    target_date: Optional[date] = None
    progress_percent: Optional[int] = Field(None, ge=0, le=100)

class GoalResponse(GoalBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Tasks ---

class TaskBase(BaseModel):
    goal_id: Optional[str] = None
    title: str = Field(..., max_length=200)
    is_completed: Optional[bool] = False
    status: Optional[Literal["PENDING", "IN_PROGRESS", "DONE"]] = Field("PENDING")
    due_date: Optional[date] = None
    pomodoro_sessions: Optional[int] = Field(0, ge=0)

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    goal_id: Optional[str] = None
    title: Optional[str] = Field(None, max_length=200)
    is_completed: Optional[bool] = None
    status: Optional[Literal["PENDING", "IN_PROGRESS", "DONE"]] = None
    due_date: Optional[date] = None
    pomodoro_sessions: Optional[int] = Field(None, ge=0)

class TaskResponse(TaskBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Planner ---

class PlannerBase(BaseModel):
    title: str = Field(..., max_length=200)
    plan_date: date
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_completed: Optional[bool] = False

class PlannerCreate(PlannerBase):
    pass

class PlannerUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    plan_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_completed: Optional[bool] = None

class PlannerResponse(PlannerBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True
