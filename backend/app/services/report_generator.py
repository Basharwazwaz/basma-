"""
AI Weekly Report Generator
Aggregates weekly data and generates a comprehensive summary.
"""

import uuid
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.health import DigitalHabits, Mood
from app.models.productivity import Tasks
from app.models.analytics import WeeklyReports


@dataclass
class WeeklyReportData:
    start_date: date
    end_date: date
    metrics_summary: dict
    ai_summary: str


async def generate_weekly_report(
    db: AsyncSession,
    user_id: uuid.UUID,
    target_week_end: Optional[date] = None,
) -> WeeklyReportData:
    """
    Generate a weekly report for the user.
    If target_week_end is None, uses the most recent Sunday.
    """

    if target_week_end is None:
        today = date.today()
        # Find the most recent Sunday
        days_since_sunday = (today.weekday() + 1) % 7
        target_week_end = today - timedelta(days=days_since_sunday) if days_since_sunday > 0 else today

    target_week_start = target_week_end - timedelta(days=6)
    prev_week_start = target_week_start - timedelta(days=7)
    prev_week_end = target_week_start - timedelta(days=1)

    # ── Fetch current week data ────────────────────────────────────────────
    curr_habits = await _fetch_habits(db, user_id, target_week_start, target_week_end)
    curr_moods = await _fetch_moods(db, user_id, target_week_start, target_week_end)
    curr_tasks = await _fetch_tasks(db, user_id, target_week_start, target_week_end)

    # ── Fetch previous week data ───────────────────────────────────────────
    prev_habits = await _fetch_habits(db, user_id, prev_week_start, prev_week_end)
    prev_moods = await _fetch_moods(db, user_id, prev_week_start, prev_week_end)
    prev_tasks = await _fetch_tasks(db, user_id, prev_week_start, prev_week_end)

    # ── Calculate metrics ──────────────────────────────────────────────────
    metrics = _calculate_metrics(curr_habits, curr_moods, curr_tasks, prev_habits, prev_moods, prev_tasks)

    # ── Generate AI summary text ───────────────────────────────────────────
    summary = _generate_summary_text(metrics)

    return WeeklyReportData(
        start_date=target_week_start,
        end_date=target_week_end,
        metrics_summary=metrics,
        ai_summary=summary,
    )


async def _fetch_habits(db, user_id, start, end):
    result = await db.execute(
        select(DigitalHabits).where(
            DigitalHabits.user_id == user_id,
            DigitalHabits.record_date >= start,
            DigitalHabits.record_date <= end,
        )
    )
    return result.scalars().all()


async def _fetch_moods(db, user_id, start, end):
    result = await db.execute(
        select(Mood).where(
            Mood.user_id == user_id,
            Mood.record_date >= start,
            Mood.record_date <= end,
        )
    )
    return result.scalars().all()


async def _fetch_tasks(db, user_id, start, end):
    result = await db.execute(
        select(Tasks).where(
            Tasks.user_id == user_id,
            Tasks.created_at >= start.isoformat(),
            Tasks.created_at <= (end + timedelta(days=1)).isoformat(),
        )
    )
    return result.scalars().all()


def _calculate_metrics(curr_habits, curr_moods, curr_tasks, prev_habits, prev_moods, prev_tasks):
    metrics = {}

    # Current week averages
    if curr_habits:
        metrics["avg_screen_time_min"] = round(sum(h.screen_time_minutes for h in curr_habits) / len(curr_habits))
        metrics["avg_social_media_min"] = round(sum(h.social_media_minutes for h in curr_habits) / len(curr_habits))
        metrics["avg_sleep_min"] = round(sum(h.sleep_minutes for h in curr_habits) / len(curr_habits))
        metrics["days_tracked"] = len(curr_habits)
    else:
        metrics["avg_screen_time_min"] = 0
        metrics["avg_social_media_min"] = 0
        metrics["avg_sleep_min"] = 0
        metrics["days_tracked"] = 0

    if curr_moods:
        metrics["avg_mood_score"] = round(sum(m.mood_score for m in curr_moods) / len(curr_moods), 1)
        metrics["avg_stress_score"] = round(sum(m.stress_score for m in curr_moods) / len(curr_moods), 1)
    else:
        metrics["avg_mood_score"] = 5.0
        metrics["avg_stress_score"] = 5.0

    # Task metrics
    metrics["total_tasks"] = len(curr_tasks)
    metrics["completed_tasks"] = sum(1 for t in curr_tasks if t.is_completed)
    metrics["completion_rate"] = (
        round((metrics["completed_tasks"] / metrics["total_tasks"]) * 100)
        if metrics["total_tasks"] > 0 else 0
    )

    # Comparison with previous week
    if prev_habits:
        prev_avg_screen = round(sum(h.screen_time_minutes for h in prev_habits) / len(prev_habits))
        metrics["screen_time_change_pct"] = (
            round(((metrics["avg_screen_time_min"] - prev_avg_screen) / max(prev_avg_screen, 1)) * 100)
            if prev_avg_screen > 0 else 0
        )
    else:
        metrics["screen_time_change_pct"] = 0

    if prev_moods:
        prev_avg_mood = sum(m.mood_score for m in prev_moods) / len(prev_moods)
        metrics["mood_change"] = round(metrics["avg_mood_score"] - prev_avg_mood, 1)
    else:
        metrics["mood_change"] = 0.0

    return metrics


def _generate_summary_text(metrics: dict) -> str:
    lines = []

    # Screen time
    avg_screen_hrs = round(metrics.get("avg_screen_time_min", 0) / 60, 1)
    screen_change = metrics.get("screen_time_change_pct", 0)
    if screen_change < -10:
        lines.append(f"قلّلت من وقت الشاشة بنسبة {abs(screen_change)}% — أداء رائع!")
    elif screen_change > 15:
        lines.append(f"زاد وقت شاشتك بنسبة {screen_change}% هذا الأسبوع. حاول تقليله تدريجيًا.")
    else:
        lines.append(f"متوسط وقت شاشتك {avg_screen_hrs} ساعات يوميًا.")

    # Sleep
    avg_sleep_hrs = round(metrics.get("avg_sleep_min", 0) / 60, 1)
    if avg_sleep_hrs >= 7:
        lines.append(f"نومك جيد ({avg_sleep_hrs} ساعات في المتوسط).")
    elif avg_sleep_hrs > 0:
        lines.append(f"نومك {avg_sleep_hrs} ساعات فقط — حاول الوصول إلى 7-8 ساعات.")

    # Mood
    mood_change = metrics.get("mood_change", 0)
    if mood_change > 0.5:
        lines.append(f"مستوى مزاجك تحسن عن الأسبوع الماضي!")
    elif mood_change < -0.5:
        lines.append(f"لاحظنا انخفاضًا في المزاج. خصص وقتًا للراحة والنشاطات الممتعة.")

    # Tasks
    completion_rate = metrics.get("completion_rate", 0)
    total = metrics.get("total_tasks", 0)
    completed = metrics.get("completed_tasks", 0)
    if total > 0:
        lines.append(f"أكملت {completed} من {total} مهمة ({completion_rate}%).")

    # General
    days_tracked = metrics.get("days_tracked", 0)
    if days_tracked < 5:
        lines.append("سجّل بياناتك يوميًا للحصول على تحليل أدق.")

    return " ".join(lines) if lines else "لا توجد بيانات كافية لل WEEKLY report. سجّل بياناتك يوميًا."


async def save_weekly_report(
    db: AsyncSession,
    user_id: uuid.UUID,
    report_data: WeeklyReportData,
) -> WeeklyReports:
    """Persist the weekly report to the database."""
    db_report = WeeklyReports(
        user_id=user_id,
        start_date=report_data.start_date,
        end_date=report_data.end_date,
        metrics_summary=report_data.metrics_summary,
        ai_summary=report_data.ai_summary,
    )
    db.add(db_report)
    await db.commit()
    await db.refresh(db_report)
    return db_report
