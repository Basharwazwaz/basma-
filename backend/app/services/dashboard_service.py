import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.health import Mood, DigitalHabits
from app.models.productivity import Goals, Tasks
from app.models.gamification import UserChallenges
from app.schemas.dashboard import DashboardSummaryResponse


async def get_dashboard_summary(
    db: AsyncSession, user_id: uuid.UUID
) -> DashboardSummaryResponse:
    today = datetime.now(timezone.utc).date()
    seven_days_ago = today - timedelta(days=6)

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

    ar_days_short = {0: "ن", 1: "ث", 2: "ر", 3: "خ", 4: "ج", 5: "س", 6: "ح"}
    ar_days_long = {
        0: "الاثنين",
        1: "الثلاثاء",
        2: "الأربعاء",
        3: "الخميس",
        4: "الجمعة",
        5: "السبت",
        6: "الأحد",
    }

    mood_chart = []
    for i in range(7):
        curr_date = seven_days_ago + timedelta(days=i)
        val = mood_dict.get(curr_date, 5)  # neutral default
        mood_chart.append({"d": ar_days_short[curr_date.weekday()], "v": val})

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

    screen_time_avg = (
        round(total_screen / count_screen, 1) if count_screen > 0 else 0.0
    )

    # ── 3. Dynamic scores from real data ──────────────────────────────────
    avg_mood = (
        round(sum(mood_dict.values()) / len(mood_dict) * 10, 0)
        if mood_dict
        else 50
    )

    # Digital health score: based on screen time
    digital_health_score = max(0, min(100, int(100 - (screen_time_avg - 4) * 10)))

    # Learning score: based on content engagement (default neutral if no data)
    learning_score = 50

    # Productivity score: based on completed tasks vs total tasks
    tasks_result = await db.execute(
        select(Tasks).where(Tasks.user_id == user_id)
    )
    all_tasks = tasks_result.scalars().all()
    if all_tasks:
        completed = sum(1 for t in all_tasks if t.is_completed)
        productivity_score = max(0, min(100, int((completed / len(all_tasks)) * 100)))
    else:
        productivity_score = 50

    # Wellbeing score: from mood data
    wellbeing_score = int(max(0, min(100, avg_mood)))

    scores = [
        {"t": "الصحة الرقمية", "v": digital_health_score, "c": "text-primary", "i": "Activity", "to": "/digital-health"},
        {"t": "التعلّم", "v": learning_score, "c": "text-info", "i": "Brain", "to": "/learning-hub"},
        {"t": "الإنتاجية", "v": productivity_score, "c": "text-warning", "i": "TrendingUp", "to": "/planner"},
        {"t": "الرفاه", "v": wellbeing_score, "c": "text-success", "i": "Heart", "to": "/mood"},
    ]

    # ── 4. Dynamic suggestions based on user data ──────────────────────────
    suggestions = []

    if screen_time_avg > 5:
        suggestions.append({
            "t": "خذ استراحة من الشاشة",
            "d": f"متوسط وقت شاشتك {screen_time_avg} ساعة يوميًا. جرّب تمشية ١٠ دقائق.",
            "a": "انصح بالتقليص",
        })

    # Check for active challenges
    challenges_result = await db.execute(
        select(UserChallenges).where(
            UserChallenges.user_id == user_id,
            UserChallenges.status == "ACTIVE",
        )
    )
    active_challenges = challenges_result.scalars().all()
    if not active_challenges:
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

    # Pad to at least 3 suggestions
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
        mood_chart=mood_chart,
        suggestions=suggestions[:3],
    )
