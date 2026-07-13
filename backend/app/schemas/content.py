from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict


class LearningContentBase(BaseModel):
    title: str
    description: Optional[str] = None
    content_type: str
    url: Optional[str] = None
    category: Optional[str] = None
    estimated_minutes: Optional[int] = None
    tags: Optional[Any] = None
    difficulty: Optional[str] = None


class ContentCreate(LearningContentBase):
    pass


class ContentResponse(LearningContentBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LearningContentCreate(LearningContentBase):
    pass


class LearningContentResponse(LearningContentBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecommendationBase(BaseModel):
    reason: Optional[str] = None
    is_dismissed: bool = False


class RecommendationCreate(RecommendationBase):
    user_id: str
    content_id: str


class RecommendationResponse(RecommendationBase):
    id: str
    user_id: str
    content_id: str
    content: LearningContentResponse
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
