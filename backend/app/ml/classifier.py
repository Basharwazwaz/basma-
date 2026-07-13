"""
User Type Classification Model
Classifies users into profiles: Balanced, Overwhelmed Student, Digital Addict, High Performer.
Uses a trained RandomForest classifier from scikit-learn with rule-based fallback.
"""
import os
import pickle
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.health import Mood, DigitalHabits
from app.models.productivity import Goals, Tasks

MODEL_PATH = os.path.join(os.path.dirname(__file__), "trained", "classifier.pkl")

_model_cache = None


def _load_model():
    global _model_cache
    if _model_cache is not None:
        return _model_cache
    try:
        with open(MODEL_PATH, "rb") as f:
            _model_cache = pickle.load(f)
        return _model_cache
    except (FileNotFoundError, pickle.UnpicklingError, EOFError):
        return None


@dataclass
class ClassificationResult:
    user_type: str
    confidence: float
    factors: dict


async def _extract_features(db: AsyncSession, user_id: str) -> Optional[dict]:
    today = date.today()
    two_weeks_ago = today - timedelta(days=14)

    habits_result = await db.execute(
        select(DigitalHabits).where(
            DigitalHabits.user_id == user_id,
            DigitalHabits.record_date >= two_weeks_ago,
        ).order_by(DigitalHabits.record_date.desc())
    )
    habits = habits_result.scalars().all()

    mood_result = await db.execute(
        select(Mood).where(
            Mood.user_id == user_id,
            Mood.record_date >= two_weeks_ago,
        ).order_by(Mood.record_date.desc())
    )
    moods = mood_result.scalars().all()

    tasks_result = await db.execute(
        select(Tasks).where(Tasks.user_id == user_id)
    )
    tasks = tasks_result.scalars().all()

    goals_result = await db.execute(
        select(Goals).where(Goals.user_id == user_id)
    )
    goals = goals_result.scalars().all()

    if not habits and not moods and not tasks:
        return None

    if habits:
        avg_screen = sum(h.screen_time_minutes for h in habits) / len(habits)
        avg_social = sum(h.social_media_minutes for h in habits) / len(habits)
        avg_sleep = sum(h.sleep_minutes for h in habits) / len(habits)
    else:
        avg_screen, avg_social, avg_sleep = 240, 60, 420

    if moods:
        avg_mood = sum(m.mood_score for m in moods) / len(moods)
        avg_stress = sum(m.stress_score for m in moods) / len(moods)
    else:
        avg_mood, avg_stress = 5, 5

    if tasks:
        completed = sum(1 for t in tasks if t.is_completed)
        completed_ratio = completed / max(len(tasks), 1)
    else:
        completed_ratio = 0.5

    active_goals = sum(1 for g in goals if g.status in ("NOT_STARTED", "IN_PROGRESS"))

    social_ratio = avg_social / max(avg_screen, 1)
    screen_h = avg_screen / 60
    sleep_h = avg_sleep / 60

    features = {
        "screen_minutes": avg_screen,
        "social_minutes": avg_social,
        "social_ratio": social_ratio,
        "sleep_minutes": avg_sleep,
        "stress": avg_stress,
        "mood": avg_mood,
        "completed_ratio": completed_ratio,
        "active_goals": active_goals,
        "screen_hours": screen_h,
        "sleep_hours": sleep_h,
    }

    feat_array = np.array([[
        avg_screen, avg_social, social_ratio, avg_sleep,
        avg_stress, avg_mood, completed_ratio, active_goals,
    ]])

    return {"features": features, "array": feat_array}


async def _rule_based_fallback(features: dict) -> ClassificationResult:
    avg_screen = features["screen_minutes"]
    avg_stress = features["stress"]
    avg_mood = features["mood"]
    completed_ratio = features["completed_ratio"]
    avg_sleep = features["sleep_minutes"]
    screen_h = features["screen_hours"]
    active_goals = features["active_goals"]

    screen_score = max(0, min(100, int(100 - (screen_h - 4) * 15)))
    sleep_score = max(0, min(100, int(100 - abs(avg_sleep / 60 - 8) * 10)))
    mood_score = int(avg_mood * 10)
    productivity_score = int(completed_ratio * 100)
    composite = screen_score * 0.3 + sleep_score * 0.2 + mood_score * 0.25 + productivity_score * 0.25

    if screen_h >= 8 and avg_stress >= 7:
        user_type = "DIGITAL_ADDICT"
        confidence = min(1.0, 0.5 + (screen_h - 8) * 0.05 + (avg_stress - 7) * 0.05)
    elif screen_h <= 4 and completed_ratio >= 0.7 and avg_mood >= 6:
        user_type = "HIGH_PERFORMER"
        confidence = min(1.0, 0.5 + (0.7 - completed_ratio) * 0.01 + (avg_mood - 6) * 0.02)
    elif avg_stress >= 6 and completed_ratio < 0.5:
        user_type = "OVERWHELMED"
        confidence = min(1.0, 0.5 + (avg_stress - 6) * 0.05 + (0.5 - completed_ratio) * 0.02)
    else:
        user_type = "BALANCED"
        confidence = min(1.0, 0.4 + composite * 0.006)

    return ClassificationResult(
        user_type=user_type,
        confidence=round(confidence, 2),
        factors={
            "screen_time_score": screen_score,
            "sleep_score": sleep_score,
            "mood_score": mood_score,
            "stress_avg": round(avg_stress, 1),
            "productivity_score": productivity_score,
            "active_goals": active_goals,
            "avg_screen_hours": round(screen_h, 1),
            "avg_sleep_hours": round(avg_sleep / 60, 1),
            "composite_score": round(composite, 1),
        },
    )


async def classify_user(db: AsyncSession, user_id: str) -> ClassificationResult:
    extracted = await _extract_features(db, user_id)
    if extracted is None:
        return ClassificationResult(
            user_type="BALANCED",
            confidence=0.3,
            factors={"message": "بيانات غير كافية للتصنيف. سجّل بياناتك اليومية لتصنيف أفضل."}
        )

    model_data = _load_model()
    if model_data is not None:
        try:
            model = model_data["model"]
            reverse_map = model_data["reverse_map"]
            array = extracted["array"]
            pred_num = model.predict(array)[0]
            probs = model.predict_proba(array)[0]
            confidence = float(max(probs))
            user_type = reverse_map[int(pred_num)]

            return ClassificationResult(
                user_type=user_type,
                confidence=round(confidence, 2),
                factors=extracted["features"],
            )
        except Exception:
            return await _rule_based_fallback(extracted["features"])

    return await _rule_based_fallback(extracted["features"])
