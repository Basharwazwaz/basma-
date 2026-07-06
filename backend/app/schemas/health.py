from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field
import uuid

# --- Mood ---

class MoodBase(BaseModel):
    record_date: date
    mood_score: int = Field(..., ge=1, le=10)
    stress_score: int = Field(..., ge=1, le=10)
    mood_state: str = Field(..., description="EXCELLENT, GOOD, NEUTRAL, BAD, TERRIBLE")
    note: Optional[str] = Field(None, max_length=500)

class MoodCreate(MoodBase):
    pass

class MoodUpdate(BaseModel):
    mood_score: Optional[int] = Field(None, ge=1, le=10)
    stress_score: Optional[int] = Field(None, ge=1, le=10)
    mood_state: Optional[str] = None
    note: Optional[str] = Field(None, max_length=500)

class MoodResponse(MoodBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

# --- Digital Habits ---

class DigitalHabitsBase(BaseModel):
    record_date: date
    screen_time_minutes: int = Field(0, ge=0)
    social_media_minutes: int = Field(0, ge=0)
    sleep_minutes: int = Field(0, ge=0)

class DigitalHabitsCreate(DigitalHabitsBase):
    pass

class DigitalHabitsUpdate(BaseModel):
    screen_time_minutes: Optional[int] = Field(None, ge=0)
    social_media_minutes: Optional[int] = Field(None, ge=0)
    sleep_minutes: Optional[int] = Field(None, ge=0)

class DigitalHabitsResponse(DigitalHabitsBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
