from datetime import datetime, date
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict


# --- Classification ---

class ClassificationResponse(BaseModel):
    user_type: str
    confidence: float
    factors: Dict[str, Any]


# --- Risk Prediction ---

class RiskPredictionResponse(BaseModel):
    risk_level: str
    risk_score: float
    factors: Dict[str, Any]
    recommendations: List[str]


# --- Insights ---

class InsightItem(BaseModel):
    insight_type: str
    message: str
    category: str
    context_data: Optional[Dict[str, Any]] = None


class InsightResponse(BaseModel):
    insights: List[InsightItem]


# --- Weekly Report ---

class WeeklyReportGenerateResponse(BaseModel):
    id: str
    user_id: str
    start_date: date
    end_date: date
    metrics_summary: Optional[Dict[str, Any]] = None
    ai_summary: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Plan Generation ---

class PlanEventResponse(BaseModel):
    title: str
    plan_date: date
    start_time: str
    end_time: str
    event_type: str


class PlanGenerateResponse(BaseModel):
    events: List[PlanEventResponse]
    message: str


# --- Content Interactions ---

class ContentInteractionCreate(BaseModel):
    interaction_type: str  # view, like, complete, bookmark


class ContentInteractionResponse(BaseModel):
    id: str
    user_id: str
    content_id: str
    interaction_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Recommendation Generation ---

class RecommendationGenerateResponse(BaseModel):
    message: str
    count: int
