import uuid
from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import Users
from app.schemas.health import (
    MoodCreate, MoodUpdate, MoodResponse,
    DigitalHabitsCreate, DigitalHabitsUpdate, DigitalHabitsResponse,
)
from app.services import health_service

router = APIRouter()


# ---------------------------------------------------------------------------
# Mood
# ---------------------------------------------------------------------------

@router.get("/mood", response_model=List[MoodResponse])
async def get_moods(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return await health_service.get_moods(db, current_user.id, start_date, end_date)


@router.get("/mood/daily", response_model=List[MoodResponse])
async def get_mood_daily(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Get mood data for the last N days (default 7)."""
    days = max(1, min(days, 365))
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)
    return await health_service.get_moods(db, current_user.id, start_date, end_date)


@router.get("/mood/weekly", response_model=List[MoodResponse])
async def get_mood_weekly(
    weeks: int = 4,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Get mood data for the last N weeks (default 4)."""
    weeks = max(1, min(weeks, 52))
    end_date = date.today()
    start_date = end_date - timedelta(weeks=weeks)
    return await health_service.get_moods(db, current_user.id, start_date, end_date)


@router.post("/mood", response_model=MoodResponse)
async def log_mood(
    mood_in: MoodCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return await health_service.create_or_update_mood(db, current_user.id, mood_in)


@router.delete("/mood/{mood_id}")
async def delete_mood(
    mood_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    await health_service.delete_mood(db, current_user.id, mood_id)
    return {"status": "success"}


# ---------------------------------------------------------------------------
# Digital Habits
# ---------------------------------------------------------------------------

@router.get("/habits", response_model=List[DigitalHabitsResponse])
async def get_digital_habits(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return await health_service.get_digital_habits(
        db, current_user.id, start_date, end_date
    )


@router.get("/habits/daily", response_model=List[DigitalHabitsResponse])
async def get_habits_daily(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Get digital habits for the last N days (default 7)."""
    days = max(1, min(days, 365))
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)
    return await health_service.get_digital_habits(db, current_user.id, start_date, end_date)


@router.get("/habits/weekly", response_model=List[DigitalHabitsResponse])
async def get_habits_weekly(
    weeks: int = 4,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Get digital habits for the last N weeks (default 4)."""
    weeks = max(1, min(weeks, 52))
    end_date = date.today()
    start_date = end_date - timedelta(weeks=weeks)
    return await health_service.get_digital_habits(db, current_user.id, start_date, end_date)


@router.get("/habits/monthly", response_model=List[DigitalHabitsResponse])
async def get_habits_monthly(
    months: int = 3,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Get digital habits for the last N months (default 3)."""
    months = max(1, min(months, 24))
    end_date = date.today()
    start_date = end_date - timedelta(days=months * 30)
    return await health_service.get_digital_habits(db, current_user.id, start_date, end_date)


@router.post("/habits", response_model=DigitalHabitsResponse)
async def log_digital_habits(
    habits_in: DigitalHabitsCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return await health_service.create_or_update_digital_habits(
        db, current_user.id, habits_in
    )


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------
from app.schemas.health import DigitalHealthAnalyticsResponse

@router.get("/analytics", response_model=DigitalHealthAnalyticsResponse)
async def get_digital_health_analytics(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Get aggregated digital health analytics for the specified number of days."""
    days = max(1, min(days, 365))
    return await health_service.get_digital_health_analytics(db, current_user.id, days)

