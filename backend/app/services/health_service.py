import uuid
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.health import Mood, DigitalHabits
from app.schemas.health import MoodCreate, MoodUpdate, DigitalHabitsCreate, DigitalHabitsUpdate, DigitalHealthAnalyticsResponse


# ---------------------------------------------------------------------------
# Mood
# ---------------------------------------------------------------------------

async def get_moods(
    db: AsyncSession,
    user_id: uuid.UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[Mood]:
    stmt = select(Mood).where(Mood.user_id == user_id)
    if start_date:
        stmt = stmt.where(Mood.record_date >= start_date)
    if end_date:
        stmt = stmt.where(Mood.record_date <= end_date)
    stmt = stmt.order_by(Mood.record_date.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_mood_by_date(
    db: AsyncSession, user_id: uuid.UUID, record_date: date
) -> Optional[Mood]:
    result = await db.execute(
        select(Mood).where(Mood.user_id == user_id, Mood.record_date == record_date)
    )
    return result.scalars().first()


async def create_or_update_mood(
    db: AsyncSession, user_id: uuid.UUID, mood_in: MoodCreate
) -> Mood:
    db_mood = await get_mood_by_date(db, user_id, mood_in.record_date)

    if db_mood:
        for field, value in mood_in.model_dump(exclude_unset=True).items():
            setattr(db_mood, field, value)
    else:
        db_mood = Mood(user_id=user_id, **mood_in.model_dump())
        db.add(db_mood)

    await db.commit()
    await db.refresh(db_mood)
    return db_mood


async def delete_mood(
    db: AsyncSession, user_id: uuid.UUID, mood_id: uuid.UUID
) -> None:
    result = await db.execute(
        select(Mood).where(Mood.id == mood_id, Mood.user_id == user_id)
    )
    db_mood = result.scalars().first()
    if not db_mood:
        raise HTTPException(status_code=404, detail="Mood record not found")
    await db.delete(db_mood)
    await db.commit()


# ---------------------------------------------------------------------------
# Digital Habits
# ---------------------------------------------------------------------------

async def get_digital_habits(
    db: AsyncSession,
    user_id: uuid.UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[DigitalHabits]:
    stmt = select(DigitalHabits).where(DigitalHabits.user_id == user_id)
    if start_date:
        stmt = stmt.where(DigitalHabits.record_date >= start_date)
    if end_date:
        stmt = stmt.where(DigitalHabits.record_date <= end_date)
    stmt = stmt.order_by(DigitalHabits.record_date.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_digital_habits_by_date(
    db: AsyncSession, user_id: uuid.UUID, record_date: date
) -> Optional[DigitalHabits]:
    result = await db.execute(
        select(DigitalHabits).where(
            DigitalHabits.user_id == user_id,
            DigitalHabits.record_date == record_date,
        )
    )
    return result.scalars().first()


async def create_or_update_digital_habits(
    db: AsyncSession, user_id: uuid.UUID, habits_in: DigitalHabitsCreate
) -> DigitalHabits:
    db_habits = await get_digital_habits_by_date(db, user_id, habits_in.record_date)

    if db_habits:
        for field, value in habits_in.model_dump(exclude_unset=True).items():
            setattr(db_habits, field, value)
    else:
        db_habits = DigitalHabits(user_id=user_id, **habits_in.model_dump())
        db.add(db_habits)

    await db.commit()
    await db.refresh(db_habits)
    return db_habits


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

async def get_digital_health_analytics(
    db: AsyncSession, user_id: uuid.UUID, days: int
) -> DigitalHealthAnalyticsResponse:
    today = datetime.now(timezone.utc).date()
    start_date = today - timedelta(days=days - 1)
    
    # We fetch for previous period too to calculate trend
    prev_start_date = start_date - timedelta(days=days)
    prev_end_date = start_date - timedelta(days=1)

    # 1. Fetch data for current period
    habits = await get_digital_habits(db, user_id, start_date, today)
    moods = await get_moods(db, user_id, start_date, today)
    
    # 2. Fetch data for prev period
    prev_habits = await get_digital_habits(db, user_id, prev_start_date, prev_end_date)
    
    # Dict mapping for fast lookup
    habit_dict = {h.record_date: h for h in habits}
    mood_dict = {m.record_date: m for m in moods}

    ar_days_short = {0: "ن", 1: "ث", 2: "ر", 3: "خ", 4: "ج", 5: "س", 6: "ح"}

    screen_time_chart = []
    sleep_stress_chart = []
    
    total_screen = 0
    total_social = 0
    total_sleep = 0
    
    for i in range(days):
        curr_date = start_date + timedelta(days=i)
        day_str = ar_days_short[curr_date.weekday()]
        
        # Habits
        h = habit_dict.get(curr_date)
        screen_hrs = round((h.screen_time_minutes / 60.0), 1) if h else 0
        sleep_hrs = round((h.sleep_minutes / 60.0), 1) if h else 0
        social_mins = h.social_media_minutes if h else 0
        
        if h:
            total_screen += h.screen_time_minutes
            total_social += social_mins
            total_sleep += h.sleep_minutes
            
        screen_time_chart.append({"d": day_str, "h": screen_hrs})
        
        # Mood
        m = mood_dict.get(curr_date)
        stress = m.stress_score if m else 5 # default neutral
        
        sleep_stress_chart.append({
            "d": day_str,
            "sleep": sleep_hrs,
            "stress": stress
        })

    # App usage chart
    other_mins = max(0, total_screen - total_social)
    total_tracked = total_screen if total_screen > 0 else 1 # avoid div/0
    
    app_usage_chart = [
        {"name": "تواصل اجتماعي", "value": round((total_social / total_tracked) * 100), "color": "var(--chart-1)"},
        {"name": "أخرى", "value": round((other_mins / total_tracked) * 100), "color": "var(--chart-5)"}
    ]
    if total_tracked == 1:
        app_usage_chart = [
            {"name": "تواصل اجتماعي", "value": 0, "color": "var(--chart-1)"},
            {"name": "أخرى", "value": 100, "color": "var(--chart-5)"}
        ]
        
    # Scores
    # Basic logic: 4 hours screen time is good (100 score). Drops as it goes higher.
    avg_screen_current = (total_screen / days) / 60.0
    current_score = max(0, min(100, int(100 - (avg_screen_current - 4) * 10)))
    
    # Prev score
    prev_total_screen = sum(h.screen_time_minutes for h in prev_habits)
    avg_screen_prev = (prev_total_screen / days) / 60.0
    prev_score = max(0, min(100, int(100 - (avg_screen_prev - 4) * 10))) if prev_habits else current_score
    
    score_trend = current_score - prev_score

    return DigitalHealthAnalyticsResponse(
        health_score=current_score,
        score_trend=score_trend,
        screen_time_chart=screen_time_chart,
        sleep_stress_chart=sleep_stress_chart,
        app_usage_chart=app_usage_chart
    )
