"""
Addiction Risk Prediction Model
Predicts risk level of digital addiction: Low, Medium, High.
Uses rule-based heuristics derived from behavioral patterns.
"""

import uuid
from dataclasses import dataclass
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.health import DigitalHabits, Mood
from app.models.gamification import UserChallenges


@dataclass
class RiskPrediction:
    risk_level: str  # LOW, MEDIUM, HIGH
    risk_score: float  # 0.0 - 100.0
    factors: dict
    recommendations: list[str]


async def predict_addiction_risk(db: AsyncSession, user_id: uuid.UUID) -> RiskPrediction:
    """
    Predict addiction risk based on:
    - Screen time trends
    - Social media usage
    - Sleep patterns
    - Mood/stress patterns
    - Failed challenges (digital detox attempts)
    """

    today = date.today()
    thirty_days_ago = today - timedelta(days=30)
    fourteen_days_ago = today - timedelta(days=14)

    # Fetch data
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

    failed_challenges_result = await db.execute(
        select(UserChallenges).where(
            UserChallenges.user_id == user_id,
            UserChallenges.status == "FAILED",
        )
    )
    failed_challenges = failed_challenges_result.scalars().all()

    if not habits:
        return RiskPrediction(
            risk_level="MEDIUM",
            risk_score=50.0,
            factors={"message": "بيانات غير كافية. سجّل عاداتك الرقمية لمدة أسبوع على الأقل."},
            recommendations=["سجّل بياناتك اليومية للحصول على تحليل دقيق"],
        )

    # ── Factor 1: Average screen time (weight: 0.30) ──────────────────────
    avg_screen = sum(h.screen_time_minutes for h in habits) / len(habits)
    # Score: 0-240 min = 0-50 risk, 240-480 = 50-80 risk, 480+ = 80-100 risk
    screen_risk = min(100, max(0, (avg_screen - 120) / 4.0))

    # ── Factor 2: Social media ratio (weight: 0.25) ───────────────────────
    avg_social = sum(h.social_media_minutes for h in habits) / len(habits)
    social_ratio = avg_social / max(avg_screen, 1)
    # High social media ratio = higher risk
    social_risk = min(100, max(0, social_ratio * 120))

    # ── Factor 3: Sleep deprivation (weight: 0.20) ────────────────────────
    avg_sleep = sum(h.sleep_minutes for h in habits) / len(habits)
    # Less sleep = higher risk. 480 min (8h) = 0 risk, 240 min (4h) = 100 risk
    sleep_risk = min(100, max(0, (480 - avg_sleep) / 2.4))

    # ── Factor 4: Stress level (weight: 0.15) ─────────────────────────────
    if moods:
        avg_stress = sum(m.stress_score for m in moods) / len(moods)
        stress_risk = min(100, max(0, (avg_stress - 3) * 14.3))
    else:
        stress_risk = 30.0

    # ── Factor 5: Failed detox challenges (weight: 0.10) ──────────────────
    challenge_risk = min(100, len(failed_challenges) * 25.0)

    # ── Composite risk score ───────────────────────────────────────────────
    risk_score = (
        screen_risk * 0.30
        + social_risk * 0.25
        + sleep_risk * 0.20
        + stress_risk * 0.15
        + challenge_risk * 0.10
    )
    risk_score = round(min(100, max(0, risk_score)), 1)

    # ── Risk level ─────────────────────────────────────────────────────────
    if risk_score >= 65:
        risk_level = "HIGH"
    elif risk_score >= 35:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # ── Generate recommendations ───────────────────────────────────────────
    recs = []
    if avg_screen > 360:
        recs.append("قلّل من وقت الشاشة إلى أقل من 6 ساعات يوميًا")
    if social_ratio > 0.5:
        recs.append("نسبة استخدام وسائل التواصل عالية. خصّص أوقاتًا محددة للتصفح")
    if avg_sleep < 420:
        recs.append("حاول النوم 7 ساعات على الأقل لتحسين صحتك الرقمية")
    if stress_risk > 50:
        recs.append("مارس تمارين الاسترخاء أو التأمل لخفض التوتر")
    if failed_challenges:
        recs.append("حاول تحدي إيقاف الشاشة مرة أخرى — الإعادة تبني العادة")
    if not recs:
        recs.append("ممتاز! حافظ على عاداتك الرقمية الصحية")

    factors = {
        "avg_screen_minutes": round(avg_screen, 0),
        "avg_social_minutes": round(avg_social, 0),
        "social_ratio": round(social_ratio, 2),
        "avg_sleep_minutes": round(avg_sleep, 0),
        "screen_risk": round(screen_risk, 1),
        "social_risk": round(social_risk, 1),
        "sleep_risk": round(sleep_risk, 1),
        "stress_risk": round(stress_risk, 1),
        "challenge_risk": round(challenge_risk, 1),
        "failed_challenges": len(failed_challenges),
    }

    return RiskPrediction(
        risk_level=risk_level,
        risk_score=risk_score,
        factors=factors,
        recommendations=recs,
    )
