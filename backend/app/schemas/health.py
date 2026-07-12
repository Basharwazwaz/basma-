from typing import Literal, Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field
import uuid

# --- Mood ---

class MoodBase(BaseModel):
    record_date: date
    mood_score: int = Field(..., ge=1, le=10)
    stress_score: int = Field(..., ge=1, le=10)
    mood_state: Literal["EXCELLENT", "GOOD", "NEUTRAL", "BAD", "TERRIBLE"] = Field(..., description="EXCELLENT, GOOD, NEUTRAL, BAD, TERRIBLE")
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

# --- Analytics ---

class ScreenTimeData(BaseModel):
    d: str
    h: float

class SleepStressData(BaseModel):
    d: str
    sleep: float
    stress: int

class AppUsageData(BaseModel):
    name: str
    value: float
    color: str

class DigitalHealthAnalyticsResponse(BaseModel):
    health_score: int
    score_trend: int
    screen_time_chart: List[ScreenTimeData]
    sleep_stress_chart: List[SleepStressData]
    app_usage_chart: List[AppUsageData]
