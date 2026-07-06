from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import date

class ScoreItem(BaseModel):
    t: str
    v: int
    c: str
    i: str
    to: str

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
    mood_chart: List[ChartData]
    suggestions: List[SuggestionItem]
