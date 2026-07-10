"""
User Type Classification Model
Classifies users into profiles: Balanced, Overwhelmed Student, Digital Addict, High Performer.
Uses a rule-based heuristic approach with optional ML enhancement.
"""

import uuid
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.health import Mood, DigitalHabits
from app.models.productivity import Goals, Tasks


@dataclass
class ClassificationResult:
    user_type: str  # BALANCED, OVERWHELMED, DIGITAL_ADDICT, HIGH_PERFORMER
    confidence: float  # 0.0 - 1.0
    factors: dict  # breakdown of contributing factors


async def classify_user(db: AsyncSession, user_id: uuid.UUID) -> ClassificationResult:
    """
    Classify a user based on their data patterns.
    
    Scoring:
    - Screen time score (0-100, lower is better)
    - Sleep score (0-100, higher is better)
    - Mood score (0-100, higher is better)
    - Productivity score (0-100, higher is better)
    """

    # Gather recent data (last 14 days)
    from datetime import date, timedelta, timezone
    today = date.today()
    two_weeks_ago = today - timedelta(days=14)
    week_ago = today - timedelta(days=7)

    # Fetch digital habits
    habits_result = await db.execute(
        select(DigitalHabits).where(
            DigitalHabits.user_id == user_id,
            DigitalHabits.record_date >= two_weeks_ago,
        ).order_by(DigitalHabits.record_date.desc())
    )
    habits = habits_result.scalars().all()

    # Fetch mood
    mood_result = await db.execute(
        select(Mood).where(
            Mood.user_id == user_id,
            Mood.record_date >= two_weeks_ago,
        ).order_by(Mood.record_date.desc())
    )
    moods = mood_result.scalars().all()

    # Fetch tasks
    tasks_result = await db.execute(
        select(Tasks).where(Tasks.user_id == user_id)
    )
    tasks = tasks_result.scalars().all()

    # Fetch goals
    goals_result = await db.execute(
        select(Goals).where(Goals.user_id == user_id)
    )
    goals = goals_result.scalars().all()

    # Default scores for new users with no data
    if not habits and not moods and not tasks:
        return ClassificationResult(
            user_type="BALANCED",
            confidence=0.3,
            factors={"message": "بيانات غير كافية للتصنيف. سجّل بياناتك اليومية لتصنيف أفضل."}
        )

    # ── Calculate screen time score ────────────────────────────────────────
    # 4 hours (240 min) = perfect, each extra hour costs 15 points
    if habits:
        avg_screen = sum(h.screen_time_minutes for h in habits) / len(habits) / 60.0
    else:
        avg_screen = 4.0  # neutral default
    screen_score = max(0, min(100, int(100 - (avg_screen - 4) * 15)))

    # ── Calculate sleep score ──────────────────────────────────────────────
    # 8 hours (480 min) = perfect, deviation costs points
    if habits:
        avg_sleep = sum(h.sleep_minutes for h in habits) / len(habits) / 60.0
    else:
        avg_sleep = 7.0  # neutral default
    sleep_score = max(0, min(100, int(100 - abs(avg_sleep - 8) * 10)))

    # ── Calculate mood score ───────────────────────────────────────────────
    if moods:
        avg_mood = sum(m.mood_score for m in moods) / len(moods)
        avg_stress = sum(m.stress_score for m in moods) / len(moods)
        mood_score = int(avg_mood * 10)
        stress_avg = avg_stress
    else:
        mood_score = 50
        stress_avg = 5.0

    # ── Calculate productivity score ───────────────────────────────────────
    if tasks:
        completed = sum(1 for t in tasks if t.is_completed)
        productivity_score = int((completed / len(tasks)) * 100)
    else:
        productivity_score = 50

    # Goal engagement
    active_goals = sum(1 for g in goals if g.status in ("NOT_STARTED", "IN_PROGRESS"))

    # ── Classification Logic ───────────────────────────────────────────────
    composite = (screen_score * 0.3 + sleep_score * 0.2 + mood_score * 0.25 + productivity_score * 0.25)

    if avg_screen >= 8 and stress_avg >= 7:
        user_type = "DIGITAL_ADDICT"
        confidence = min(1.0, 0.5 + (avg_screen - 8) * 0.05 + (stress_avg - 7) * 0.05)
    elif avg_screen <= 4 and productivity_score >= 70 and mood_score >= 60:
        user_type = "HIGH_PERFORMER"
        confidence = min(1.0, 0.5 + (70 - productivity_score) * 0.01 + (mood_score - 60) * 0.01)
    elif stress_avg >= 6 and productivity_score < 50:
        user_type = "OVERWHELMED"
        confidence = min(1.0, 0.5 + (stress_avg - 6) * 0.05 + (50 - productivity_score) * 0.01)
    else:
        user_type = "BALANCED"
        confidence = min(1.0, 0.4 + composite * 0.006)

    factors = {
        "screen_time_score": screen_score,
        "sleep_score": sleep_score,
        "mood_score": mood_score,
        "stress_avg": round(stress_avg, 1),
        "productivity_score": productivity_score,
        "active_goals": active_goals,
        "avg_screen_hours": round(avg_screen, 1),
        "avg_sleep_hours": round(avg_sleep, 1),
        "composite_score": round(composite, 1),
    }

    return ClassificationResult(
        user_type=user_type,
        confidence=round(confidence, 2),
        factors=factors,
    )
