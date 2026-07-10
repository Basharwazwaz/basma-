"""
AI Insight Engine
Analyzes correlations in user data and generates actionable insights.
E.g., "You used Instagram for 5 hours daily, which correlates with a 30% decrease in study time."
"""

import uuid
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.health import DigitalHabits, Mood
from app.models.productivity import Tasks, Goals
from app.models.analytics import AIInsights


@dataclass
class Insight:
    insight_type: str  # WARNING, PRAISE, TIP, CORRELATION
    message: str
    category: str  # digital_health, study, mood, career
    context_data: dict


async def generate_insights(db: AsyncSession, user_id: uuid.UUID) -> List[Insight]:
    """Analyze user data patterns and generate personalized insights."""
    insights: List[Insight] = []

    today = date.today()
    fourteen_days_ago = today - timedelta(days=14)
    seven_days_ago = today - timedelta(days=7)
    prev_week_start = today - timedelta(days=13)
    prev_week_end = today - timedelta(days=7)

    # Fetch data
    habits_result = await db.execute(
        select(DigitalHabits).where(
            DigitalHabits.user_id == user_id,
            DigitalHabits.record_date >= fourteen_days_ago,
        ).order_by(DigitalHabits.record_date.asc())
    )
    habits = habits_result.scalars().all()

    mood_result = await db.execute(
        select(Mood).where(
            Mood.user_id == user_id,
            Mood.record_date >= fourteen_days_ago,
        ).order_by(Mood.record_date.asc())
    )
    moods = mood_result.scalars().all()

    tasks_result = await db.execute(
        select(Tasks).where(Tasks.user_id == user_id)
    )
    tasks = tasks_result.scalars().all()

    if not habits and not moods:
        insights.append(Insight(
            insight_type="TIP",
            message="ابدأ بتسجيل بياناتك اليومية للحصول على رؤى ذكية مخصصة لك!",
            category="digital_health",
            context_data={},
        ))
        return insights

    # ── Insight 1: Screen time trend ───────────────────────────────────────
    current_week_habits = [h for h in habits if h.record_date >= seven_days_ago]
    prev_week_habits = [h for h in habits if prev_week_start <= h.record_date <= prev_week_end]

    if current_week_habits and prev_week_habits:
        curr_avg = sum(h.screen_time_minutes for h in current_week_habits) / len(current_week_habits)
        prev_avg = sum(h.screen_time_minutes for h in prev_week_habits) / len(prev_week_habits)
        change_pct = ((curr_avg - prev_avg) / max(prev_avg, 1)) * 100

        if change_pct < -15:
            insights.append(Insight(
                insight_type="PRAISE",
                message=f"أحسنت! قلّلت من وقت الشاشة بنسبة {abs(int(change_pct))}% هذا الأسبوع مقارنة بالأسبوع الماضي.",
                category="digital_health",
                context_data={"change_pct": round(change_pct, 1), "metric": "screen_time"},
            ))
        elif change_pct > 20:
            insights.append(Insight(
                insight_type="WARNING",
                message=f"زاد وقت شاشتك بنسبة {int(change_pct)}% هذا الأسبوع. حاول تخصيص أوقات محددة للجهاز.",
                category="digital_health",
                context_data={"change_pct": round(change_pct, 1), "metric": "screen_time"},
            ))

    # ── Insight 2: Screen time vs mood correlation ─────────────────────────
    if habits and moods:
        habit_by_date = {h.record_date: h for h in habits}
        mood_by_date = {m.record_date: m for m in moods}
        common_dates = set(habit_by_date.keys()) & set(mood_by_date.keys())

        if len(common_dates) >= 3:
            high_screen_moods = []
            low_screen_moods = []
            threshold = sum(h.screen_time_minutes for h in habits) / len(habits)

            for d in common_dates:
                if habit_by_date[d].screen_time_minutes > threshold:
                    high_screen_moods.append(mood_by_date[d].mood_score)
                else:
                    low_screen_moods.append(mood_by_date[d].mood_score)

            if high_screen_moods and low_screen_moods:
                avg_high = sum(high_screen_moods) / len(high_screen_moods)
                avg_low = sum(low_screen_moods) / len(low_screen_moods)
                diff = avg_low - avg_high

                if diff > 1:
                    insights.append(Insight(
                        insight_type="CORRELATION",
                        message=f"أيام الشاشة العالية ترتبط بمزاج أقل. في الأيام قليلة الشاشة، مزاجك أعلى بـ {diff:.1f} نقاط في المتوسط.",
                        category="mood",
                        context_data={"high_screen_mood": round(avg_high, 1), "low_screen_mood": round(avg_low, 1)},
                    ))

    # ── Insight 3: Sleep quality impact ────────────────────────────────────
    if habits:
        avg_sleep = sum(h.sleep_minutes for h in habits) / len(habits) / 60.0
        if avg_sleep < 6:
            insights.append(Insight(
                insight_type="WARNING",
                message=f"متوسط نومك {avg_sleep:.1f} ساعات فقط. النوم Less من 7 ساعات يضعف التركيز والإنتاجية.",
                category="digital_health",
                context_data={"avg_sleep_hours": round(avg_sleep, 1)},
            ))
        elif avg_sleep >= 7.5:
            insights.append(Insight(
                insight_type="PRAISE",
                message=f"نومك ممتاز! {avg_sleep:.1f} ساعات في المتوسط. هذا يدعم صحتك وتركيزك.",
                category="digital_health",
                context_data={"avg_sleep_hours": round(avg_sleep, 1)},
            ))

    # ── Insight 4: Task completion rate ────────────────────────────────────
    if tasks:
        completed = sum(1 for t in tasks if t.is_completed)
        total = len(tasks)
        rate = (completed / total) * 100

        if rate >= 80:
            insights.append(Insight(
                insight_type="PRAISE",
                message=f"معدل إنجاز مهامك {int(rate)}% — أداء ممتاز! استمر في هذا الإيقاع.",
                category="study",
                context_data={"completion_rate": round(rate, 1)},
            ))
        elif rate < 30 and total > 3:
            insights.append(Insight(
                insight_type="TIP",
                message=f"أكملت {completed} من {total} مهام فقط ({int(rate)}%). جرّب تقسيم المهام الكبيرة إلى أجزاء أصغر.",
                category="study",
                context_data={"completion_rate": round(rate, 1)},
            ))

    # ── Insight 5: Social media dominance ──────────────────────────────────
    if habits:
        avg_social = sum(h.social_media_minutes for h in habits) / len(habits)
        avg_screen = sum(h.screen_time_minutes for h in habits) / len(habits)
        ratio = avg_social / max(avg_screen, 1)

        if ratio > 0.6:
            insights.append(Insight(
                insight_type="WARNING",
                message=f"وسائل التواصل تستهلك {int(ratio * 100)}% من وقت شاشتك. حاول تخصيص أوقات محددة للتصفح.",
                category="digital_health",
                context_data={"social_ratio": round(ratio, 2)},
            ))

    # Limit to top 5 insights
    return insights[:5]


async def save_insights(
    db: AsyncSession,
    user_id: uuid.UUID,
    insights: List[Insight],
) -> List[AIInsights]:
    """Persist insights to the database."""
    saved = []
    for ins in insights:
        db_insight = AIInsights(
            user_id=user_id,
            insight_type=ins.insight_type,
            message=ins.message,
            context_data=ins.context_data,
        )
        db.add(db_insight)
        saved.append(db_insight)

    await db.commit()
    for ins in saved:
        await db.refresh(ins)
    return saved


async def get_latest_insights(
    db: AsyncSession,
    user_id: uuid.UUID,
    limit: int = 10,
) -> List[AIInsights]:
    """Get the most recent insights for a user."""
    result = await db.execute(
        select(AIInsights)
        .where(AIInsights.user_id == user_id)
        .order_by(AIInsights.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()
