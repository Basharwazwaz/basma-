from typing import Literal, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

# --- Challenges ---

class ChallengeBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=50)
    duration_days: int = Field(7, ge=1)
    points_reward: int = Field(0, ge=0)

class ChallengeResponse(ChallengeBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

# --- User Challenges ---

class UserChallengeBase(BaseModel):
    challenge_id: uuid.UUID
    status: Literal["ACTIVE", "COMPLETED", "FAILED"] = Field("ACTIVE", description="ACTIVE, COMPLETED, FAILED")
    progress_days: int = Field(0, ge=0)

class UserChallengeCreate(BaseModel):
    challenge_id: uuid.UUID

class UserChallengeUpdate(BaseModel):
    status: Optional[Literal["ACTIVE", "COMPLETED", "FAILED"]] = None

class UserChallengeResponse(UserChallengeBase):
    id: uuid.UUID
    user_id: uuid.UUID
    started_at: datetime
    completed_at: Optional[datetime] = None
    last_checkin: Optional[datetime] = None
    challenge: Optional[ChallengeResponse] = None

    class Config:
        from_attributes = True

# --- Achievements ---

class AchievementBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=50)

class AchievementCreate(AchievementBase):
    pass

class AchievementResponse(AchievementBase):
    id: uuid.UUID
    user_id: uuid.UUID
    earned_at: datetime

    class Config:
        from_attributes = True
