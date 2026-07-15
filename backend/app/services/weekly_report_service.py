import uuid
import json
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.models.analytics import WeeklyReports
from app.models.health import Mood, DigitalHabits
from app.models.productivity import Goals, Tasks
from app.models.content import UserContentInteraction, LearningContent


async def get_weekly_reports(
    db: AsyncSession, user_id: uuid.UUID
) -> List[WeeklyReports]:
    """Return all weekly reports for a user, newest first."""
    result = await db.execute(
        select(WeeklyReports)
        .where(WeeklyReports.user_id == user_id)
        .order_by(WeeklyReports.start_date.desc())
    )
    return result.scalars().all()


async def generate_weekly_report(
    db: AsyncSession, user_id: uuid.UUID,
) -> WeeklyReports:
    """Compute and save a weekly report for the past 7 days."""
    today = datetime.now(timezone.utc).date()
    end_date = today
    start_date = today - timedelta(days=6)
    prev_start = start_date - timedelta(days=7)
    prev_end = start_date - timedelta(days=1)

    # ── Screen time ─────────────────────────────────────────────────────
    curr_screen = await db.scalar(
        select(func.avg(DigitalHabits.screen_time_minutes)).where(
            DigitalHabits.user_id == user_id,
            DigitalHabits.record_date >= start_date,
            DigitalHabits.record_date <= end_date,
        )
    ) or 0
    prev_screen = await db.scalar(
        select(func.avg(DigitalHabits.screen_time_minutes)).where(
            DigitalHabits.user_id == user_id,
            DigitalHabits.record_date >= prev_start,
            DigitalHabits.record_date <= prev_end,
        )
    ) or 0

    # ── Mood ─────────────────────────────────────────────────────────────
    moods = await db.execute(
        select(Mood.mood_score).where(
            Mood.user_id == user_id,
            Mood.record_date >= start_date,
            Mood.record_date <= end_date,
        )
    )
    mood_scores = moods.scalars().all()
    avg_mood = round(sum(mood_scores) / len(mood_scores), 1) if mood_scores else 0

    # ── Tasks ─────────────────────────────────────────────────────────────
    all_tasks = await db.execute(select(Tasks).where(Tasks.user_id == user_id))
    tasks_list = all_tasks.scalars().all()
    total_tasks = len(tasks_list)
    completed_tasks = sum(1 for t in tasks_list if t.is_completed)

    # ── Goals ─────────────────────────────────────────────────────────────
    goals = await db.execute(select(Goals).where(Goals.user_id == user_id))
    goals_list = goals.scalars().all()
    completed_goals = sum(1 for g in goals_list if g.status == "COMPLETED")

    # ── Content ───────────────────────────────────────────────────────────
    completed_content = await db.scalar(
        select(func.count(UserContentInteraction.id)).where(
            UserContentInteraction.user_id == user_id,
            UserContentInteraction.interaction_type == "complete",
        )
    ) or 0

    # ── Day-by-day screen time comparison ─────────────────────────────────
    screen_time_comparison = []
    days_ar = ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"]
    for offset in range(7):
        day = start_date + timedelta(days=offset)
        prev_day = day - timedelta(days=7)
        curr_val = await db.scalar(
            select(func.coalesce(func.avg(DigitalHabits.screen_time_minutes), 0)).where(
                DigitalHabits.user_id == user_id,
                DigitalHabits.record_date == day,
            )
        )
        prev_val = await db.scalar(
            select(func.coalesce(func.avg(DigitalHabits.screen_time_minutes), 0)).where(
                DigitalHabits.user_id == user_id,
                DigitalHabits.record_date == prev_day,
            )
        )
        day_name = days_ar[day.weekday()]
        # Shift so Saturday (5) → index 6, Sunday (6) → 0
        screen_time_comparison.append({
            "name": day_name,
            "thisWeek": round((curr_val or 0) / 60.0, 1),
            "lastWeek": round((prev_val or 0) / 60.0, 1),
        })

    # ── Build metrics ─────────────────────────────────────────────────────
    screen_time_hrs = round(curr_screen / 60.0, 1) if curr_screen else 0
    prev_screen_hrs = round(prev_screen / 60.0, 1) if prev_screen else 0
    health_score = max(0, min(100, int(100 - (screen_time_hrs - 4) * 10)))
    wellbeing_score = int(max(0, min(100, avg_mood * 10))) if mood_scores else 0
    productivity_score = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
    learning_score = min(100, completed_content * 10)

    metrics_summary = {
        "screen_time_avg_hrs": screen_time_hrs,
        "screen_time_prev_hrs": prev_screen_hrs,
        "screen_time_change_pct": round(((screen_time_hrs - prev_screen_hrs) / prev_screen_hrs) * 100, 1) if prev_screen_hrs > 0 else 0,
        "mood_avg": avg_mood,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "productivity_pct": productivity_score,
        "completed_goals": completed_goals,
        "total_goals": len(goals_list),
        "health_score": health_score,
        "wellbeing_score": wellbeing_score,
        "learning_score": learning_score,
        "completed_content": completed_content,
        "screen_time_comparison": screen_time_comparison,
    }

    # ── Build AI summary ─────────────────────────────────────────────────
    summary_parts = []
    if screen_time_hrs > 5:
        summary_parts.append(f"⚠️ وقت الشاشة مرتفع ({screen_time_hrs} س/يوم). حاول التقليل.")
    elif screen_time_hrs < 3:
        summary_parts.append(f"✅ وقت شاشتك ممتاز ({screen_time_hrs} س/يوم). استمر!")
    if avg_mood >= 7:
        summary_parts.append(f"😊 مزاجك جيد هذا الأسبوع (معدل {avg_mood}/10). حافظ على إيجابيتك.")
    elif avg_mood < 4 and mood_scores:
        summary_parts.append(f"😔 مزاجك منخفض (معدل {avg_mood}/10). جرّب أنشطة الاسترخاء.")
    if productivity_score >= 70:
        summary_parts.append(f"🎯 إنتاجيتك عالية ({completed_tasks}/{total_tasks} مهام مكتملة).")
    elif total_tasks > 0 and productivity_score < 30:
        summary_parts.append(f"📋 نسبة إنجاز المهام {productivity_score}%. حدّد أولوياتك.")

    ai_summary = " ".join(summary_parts) if summary_parts else "📊 استمر في تسجيل بياناتك للحصول على تحليل أسبوعي دقيق."

    # ── Save ──────────────────────────────────────────────────────────────
    report = WeeklyReports(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        metrics_summary=metrics_summary,
        ai_summary=ai_summary,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report
