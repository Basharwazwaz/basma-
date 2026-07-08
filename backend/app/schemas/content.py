import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class LearningContentBase(BaseModel):
    title: str
    description: Optional[str] = None
    content_type: str
    url: Optional[str] = None
    category: Optional[str] = None
    estimated_minutes: Optional[int] = None


class LearningContentCreate(LearningContentBase):
    pass


class LearningContentResponse(LearningContentBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecommendationBase(BaseModel):
    reason: Optional[str] = None
    is_dismissed: bool = False


class RecommendationCreate(RecommendationBase):
    user_id: uuid.UUID
    content_id: uuid.UUID


class RecommendationResponse(RecommendationBase):
    id: uuid.UUID
    user_id: uuid.UUID
    content_id: uuid.UUID
    content: LearningContentResponse
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
