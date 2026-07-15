from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import date

class ScoreItem(BaseModel):
    t: str
    v: int
    c: str
    i: str
    to: str
    trend: int = 0  # percentage change vs previous period

class ChartData(BaseModel):
    d: str
    h: Optional[float] = None
    v: Optional[float] = None

class SuggestionItem(BaseModel):
    t: str
    d: str
    a: str

class DashboardSummaryResponse(BaseModel):
    scores: List[ScoreItem]
    screen_time: List[ChartData]
    screen_time_avg: float
    screen_time_trend: int = 0  # percentage change vs previous week
    mood_chart: List[ChartData]
    suggestions: List[SuggestionItem]
