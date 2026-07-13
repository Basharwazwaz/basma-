from datetime import datetime, date
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class WeeklyReportBase(BaseModel):
    start_date: date
    end_date: date
    metrics_summary: Optional[Dict[str, Any]] = None
    ai_summary: Optional[str] = None


class WeeklyReportCreate(WeeklyReportBase):
    pass


class WeeklyReportResponse(WeeklyReportBase):
    id: str
    user_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIInsightBase(BaseModel):
    insight_type: str
    message: str
    context_data: Optional[Dict[str, Any]] = None


class AIInsightCreate(AIInsightBase):
    pass


class AIInsightResponse(AIInsightBase):
    id: str
    user_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
