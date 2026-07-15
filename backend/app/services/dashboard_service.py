import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.models.health import Mood, DigitalHabits
from app.models.productivity import Goals, Tasks
from app.models.gamification import UserChallenges
from app.models.content import UserContentInteraction, LearningContent
from app.schemas.dashboard import DashboardSummaryResponse


async def get_dashboard_summary(
    db: AsyncSession, user_id: uuid.UUID
) -> DashboardSummaryResponse:
    today = datetime.now(timezone.utc).date()
    seven_days_ago = today - timedelta(days=6)
    prev_week_end = seven_days_ago - timedelta(days=1)
    prev_week_start = prev_week_end - timedelta(days=6)

    ar_days_short = {0: "ن", 1: "ث", 2: "ر", 3: "خ", 4: "ج", 5: "س", 6: "ح"}
    ar_days_long = {
        0: "الاثنين", 1: "الثلاثاء", 2: "الأربعاء", 3: "الخميس",
        4: "الجمعة", 5: "السبت", 6: "الأحد",
    }

    # ── Helper: compute avg from query ──────────────────────────────────
    async def _avg_screen(start: date, end: date) -> float:
        result = await db.execute(
            select(func.avg(DigitalHabits.screen_time_minutes)).where(
                DigitalHabits.user_id == user_id,
                DigitalHabits.record_date >= start,
                DigitalHabits.record_date <= end,
            )
        )
        val = result.scalar()
        return round((val or 0) / 60.0, 1)

    # ── 1. Mood for last 7 days ───────────────────────────────────────────
    mood_result = await db.execute(
        select(Mood).where(
            Mood.user_id == user_id,
            Mood.record_date >= seven_days_ago,
            Mood.record_date <= today,
        ).order_by(Mood.record_date.asc())
    )
    moods = mood_result.scalars().all()
    mood_dict = {m.record_date: m.mood_score for m in moods}

    mood_chart = []
    for i in range(7):
        curr_date = seven_days_ago + timedelta(days=i)
        val = mood_dict.get(curr_date, 5)
        mood_chart.append({"d": ar_days_short[curr_date.weekday()], "v": val})

    avg_mood = round(sum(mood_dict.values()) / len(mood_dict) * 10, 0) if mood_dict else 50

    # ── 2. Digital Habits for last 7 days ────────────────────────────────
    habits_result = await db.execute(
        select(DigitalHabits).where(
            DigitalHabits.user_id == user_id,
            DigitalHabits.record_date >= seven_days_ago,
            DigitalHabits.record_date <= today,
        ).order_by(DigitalHabits.record_date.asc())
    )
    habits = habits_result.scalars().all()
    habit_dict = {h.record_date: h.screen_time_minutes for h in habits}

    screen_time_chart = []
    total_screen = 0.0
    count_screen = 0
    for i in range(7):
        curr_date = seven_days_ago + timedelta(days=i)
        mins = habit_dict.get(curr_date, 0)
        hrs = round(mins / 60.0, 1) if mins > 0 else 0.0
        if hrs > 0:
            total_screen += hrs
            count_screen += 1
        screen_time_chart.append(
            {"d": ar_days_long[curr_date.weekday()], "h": hrs if hrs > 0 else 0.0}
        )

    screen_time_avg = round(total_screen / count_screen, 1) if count_screen > 0 else 0.0

    # ── Previous week screen time avg for trend ─────────────────────────
    prev_avg = await _avg_screen(prev_week_start, prev_week_end)
    screen_time_trend = 0
    if prev_avg > 0:
        screen_time_trend = int(((screen_time_avg - prev_avg) / prev_avg) * 100)

    # ── 3. Dynamic scores from real data ──────────────────────────────────
    digital_health_score = max(0, min(100, int(100 - (screen_time_avg - 4) * 10)))
    prev_digital_health = max(0, min(100, int(100 - (prev_avg - 4) * 10))) if prev_avg > 0 else 50

    # Learning score: based on content interactions
    completed_content = await db.scalar(
        select(func.count(UserContentInteraction.id)).where(
            UserContentInteraction.user_id == user_id,
            UserContentInteraction.interaction_type == "complete",
        )
    )
    total_content = await db.scalar(select(func.count(LearningContent.id)))
    if total_content and total_content > 0:
        learning_score = min(100, int((completed_content / total_content) * 100))
    else:
        learning_score = 0
    prev_learning = 0  # no historical tracking for content interactions yet

    # Productivity score: based on completed tasks
    tasks_result = await db.execute(select(Tasks).where(Tasks.user_id == user_id))
    all_tasks = tasks_result.scalars().all()
    if all_tasks:
        completed = sum(1 for t in all_tasks if t.is_completed)
        productivity_score = max(0, min(100, int((completed / len(all_tasks)) * 100)))
    else:
        productivity_score = 0
    # Previous period tasks
    prev_tasks_result = await db.execute(
        select(Tasks).where(
            Tasks.user_id == user_id,
            Tasks.updated_at >= prev_week_start,
            Tasks.updated_at <= prev_week_end,
        )
    )
    prev_tasks = prev_tasks_result.scalars().all()
    prev_productivity = max(0, min(100, int((sum(1 for t in prev_tasks if t.is_completed) / len(prev_tasks)) * 100))) if prev_tasks else 0

    # Wellbeing score: from mood
    wellbeing_score = int(max(0, min(100, avg_mood)))
    # Previous period mood avg
    prev_mood_result = await db.execute(
        select(Mood).where(
            Mood.user_id == user_id,
            Mood.record_date >= prev_week_start,
            Mood.record_date <= prev_week_end,
        )
    )
    prev_moods = prev_mood_result.scalars().all()
    prev_wellbeing = int(max(0, min(100, round(sum(m.mood_score for m in prev_moods) / len(prev_moods) * 10, 0)))) if prev_moods else 0

    def trend(current: int, prev: int) -> int:
        if prev == 0:
            return 0
        return int(((current - prev) / prev) * 100)

    scores = [
        {"t": "الصحة الرقمية", "v": digital_health_score, "c": "text-primary", "i": "Activity", "to": "/digital-health", "trend": trend(digital_health_score, prev_digital_health)},
        {"t": "التعلّم", "v": learning_score, "c": "text-info", "i": "Brain", "to": "/learning-hub", "trend": trend(learning_score, prev_learning)},
        {"t": "الإنتاجية", "v": productivity_score, "c": "text-warning", "i": "TrendingUp", "to": "/planner", "trend": trend(productivity_score, prev_productivity)},
        {"t": "الرفاه", "v": wellbeing_score, "c": "text-success", "i": "Heart", "to": "/mood", "trend": trend(wellbeing_score, prev_wellbeing)},
    ]

    # ── 4. Dynamic suggestions based on user data ──────────────────────────
    suggestions = []

    if screen_time_avg > 5:
        suggestions.append({
            "t": "خذ استراحة من الشاشة",
            "d": f"متوسط وقت شاشتك {screen_time_avg} ساعة يوميًا. جرّب تمشية ١٠ دقائق.",
            "a": "انصح بالتقليص",
        })

    challenges_result = await db.execute(
        select(UserChallenges).where(
            UserChallenges.user_id == user_id,
            UserChallenges.status == "ACTIVE",
        )
    )
    if not challenges_result.scalars().all():
        suggestions.append({
            "t": "انضمّ لتحدي جديد",
            "d": "ليس لديك أي تحدٍّ نشط. تحدّيات تساعدك على بناء عادات إيجابية.",
            "a": "تصفح التحديات",
        })

    if not all_tasks or all(t.is_completed for t in all_tasks):
        suggestions.append({
            "t": "أضف مهام جديدة",
            "d": "أكملت كل مهامك! أضف مهام جديدة لتبقى منظّمًا.",
            "a": "أضف مهمة",
        })

    if avg_mood < 40:
        suggestions.append({
            "t": "استرخاء وتأمل",
            "d": "مستوى مزاجك منخفض. خصص ١٥ دقيقة للتأمل لرفع مستوى الرفاهية.",
            "a": "افتح التأمل",
        })

    default_suggestions = [
        {"t": "جلسة تركيز قصيرة", "d": "ابدأ جلسة بومودورو لمدة ٢٥ دقيقة لتحسين إنتاجيتك.", "a": "ابدأ الجلسة"},
        {"t": "راجع أهدافك", "d": "تأكد أن أهدافك محدّثة ومتوافقة مع خطتك.", "a": "تحديث الأهداف"},
        {"t": "مقال مقترح", "d": "اقرأ مقالًا تعليميًا جديدًا لتطوير مهاراتك.", "a": "اقرأ المقال"},
    ]
    for s in default_suggestions:
        if len(suggestions) >= 3:
            break
        if not any(existing["t"] == s["t"] for existing in suggestions):
            suggestions.append(s)

    return DashboardSummaryResponse(
        scores=scores,
        screen_time=screen_time_chart,
        screen_time_avg=screen_time_avg,
        screen_time_trend=screen_time_trend,
        mood_chart=mood_chart,
        suggestions=suggestions[:3],
    )
