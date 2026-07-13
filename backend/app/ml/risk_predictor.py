"""
Addiction Risk Prediction Model
Predicts risk level of digital addiction: Low, Medium, High.
Uses a trained GradientBoosting classifier from scikit-learn with rule-based fallback.
"""
import os
import pickle
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.health import DigitalHabits, Mood
from app.models.gamification import UserChallenges

MODEL_PATH = os.path.join(os.path.dirname(__file__), "trained", "risk_predictor.pkl")

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
class RiskPrediction:
    risk_level: str
    risk_score: float
    factors: dict
    recommendations: list[str]


async def _extract_features(db: AsyncSession, user_id: str) -> Optional[dict]:
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)

    habits_result = await db.execute(
        select(DigitalHabits).where(
            DigitalHabits.user_id == user_id,
            DigitalHabits.record_date >= thirty_days_ago,
        ).order_by(DigitalHabits.record_date.asc())
    )
    habits = habits_result.scalars().all()

    mood_result = await db.execute(
        select(Mood).where(
            Mood.user_id == user_id,
            Mood.record_date >= thirty_days_ago,
        )
    )
    moods = mood_result.scalars().all()

    failed_result = await db.execute(
        select(UserChallenges).where(
            UserChallenges.user_id == user_id,
            UserChallenges.status == "FAILED",
        )
    )
    failed_challenges = failed_result.scalars().all()

    if not habits:
        return None

    avg_screen = sum(h.screen_time_minutes for h in habits) / len(habits)
    avg_social = sum(h.social_media_minutes for h in habits) / len(habits)
    avg_sleep = sum(h.sleep_minutes for h in habits) / len(habits)
    social_ratio = avg_social / max(avg_screen, 1)
    failed_count = len(failed_challenges)

    avg_screen_risk = min(100, max(0, (avg_screen - 120) / 4.0))
    social_risk_val = min(100, max(0, social_ratio * 120))
    sleep_risk_val = min(100, max(0, (480 - avg_sleep) / 2.4))

    if moods:
        avg_stress = sum(m.stress_score for m in moods) / len(moods)
        stress_risk_val = min(100, max(0, (avg_stress - 3) * 14.3))
    else:
        avg_stress = 5.0
        stress_risk_val = 30.0

    challenge_risk_val = min(100, failed_count * 25.0)

    composite_risk = (
        avg_screen_risk * 0.30 + social_risk_val * 0.25 +
        sleep_risk_val * 0.20 + stress_risk_val * 0.15 +
        challenge_risk_val * 0.10
    )
    composite_risk = round(min(100, max(0, composite_risk)), 1)

    return {
        "avg_screen_minutes": round(avg_screen, 0),
        "avg_social_minutes": round(avg_social, 0),
        "social_ratio": round(social_ratio, 2),
        "avg_sleep_minutes": round(avg_sleep, 0),
        "avg_stress": round(avg_stress, 1),
        "failed_challenges": failed_count,
        "avg_screen_risk": round(avg_screen_risk, 1),
        "social_risk": round(social_risk_val, 1),
        "sleep_risk": round(sleep_risk_val, 1),
        "stress_risk": round(stress_risk_val, 1),
        "challenge_risk": round(challenge_risk_val, 1),
        "composite_risk": composite_risk,
        "array": np.array([[
            avg_screen, avg_social, social_ratio, avg_sleep,
            avg_stress, failed_count,
            avg_screen_risk, social_risk_val, sleep_risk_val,
            stress_risk_val, challenge_risk_val,
        ]]),
    }


async def _rule_based_fallback(features: dict) -> RiskPrediction:
    risk_score = features["composite_risk"]
    avg_screen = features["avg_screen_minutes"]
    social_ratio = features["social_ratio"]
    avg_sleep = features["avg_sleep_minutes"]
    avg_stress = features["avg_stress"]
    failed_count = features["failed_challenges"]

    if risk_score >= 65:
        risk_level = "HIGH"
    elif risk_score >= 35:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    recs = []
    if avg_screen > 360:
        recs.append("قلّل من وقت الشاشة إلى أقل من 6 ساعات يوميًا")
    if social_ratio > 0.5:
        recs.append("نسبة استخدام وسائل التواصل عالية. خصّص أوقاتًا محددة للتصفح")
    if avg_sleep < 420:
        recs.append("حاول النوم 7 ساعات على الأقل لتحسين صحتك الرقمية")
    if avg_stress > 6:
        recs.append("مارس تمارين الاسترخاء أو التأمل لخفض التوتر")
    if failed_count > 0:
        recs.append("حاول تحدي إيقاف الشاشة مرة أخرى — الإعادة تبني العادة")
    if not recs:
        recs.append("ممتاز! حافظ على عاداتك الرقمية الصحية")

    return RiskPrediction(
        risk_level=risk_level,
        risk_score=risk_score,
        factors={k: v for k, v in features.items() if k != "array"},
        recommendations=recs,
    )


async def predict_addiction_risk(db: AsyncSession, user_id: str) -> RiskPrediction:
    extracted = await _extract_features(db, user_id)
    if extracted is None:
        return RiskPrediction(
            risk_level="MEDIUM",
            risk_score=50.0,
            factors={"message": "بيانات غير كافية. سجّل عاداتك الرقمية لمدة أسبوع على الأقل."},
            recommendations=["سجّل بياناتك اليومية للحصول على تحليل دقيق"],
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
            risk_level = reverse_map[int(pred_num)]

            risk_score = round(confidence * 100, 1)
            factors = {k: v for k, v in extracted.items() if k != "array"}
            factors["ml_confidence"] = round(confidence, 2)
            factors["ml_risk_score"] = risk_score

            recs = []
            if risk_level in ("HIGH", "MEDIUM"):
                if extracted["avg_screen_minutes"] > 360:
                    recs.append("قلّل من وقت الشاشة إلى أقل من 6 ساعات يوميًا")
                if extracted["social_ratio"] > 0.5:
                    recs.append("نسبة استخدام وسائل التواصل عالية. خصّص أوقاتًا محددة للتصفح")
                if extracted["avg_sleep_minutes"] < 420:
                    recs.append("حاول النوم 7 ساعات على الأقل")
                if extracted["avg_stress"] > 6:
                    recs.append("مارس تمارين الاسترخاء أو التأمل")
                if extracted["failed_challenges"] > 0:
                    recs.append("حاول تحدي إيقاف الشاشة مرة أخرى")
            if not recs:
                recs.append("ممتاز! حافظ على عاداتك الرقمية الصحية")

            return RiskPrediction(
                risk_level=risk_level,
                risk_score=risk_score,
                factors=factors,
                recommendations=recs,
            )
        except Exception:
            return await _rule_based_fallback(extracted)

    return await _rule_based_fallback(extracted)
