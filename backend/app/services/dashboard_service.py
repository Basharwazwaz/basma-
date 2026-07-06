from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid
from datetime import datetime, timedelta, date

from app.models.health import Mood, DigitalHabits
from app.models.productivity import Tasks, Goals
from app.schemas.dashboard import DashboardSummaryResponse

def get_dashboard_summary(db: Session, user_id: uuid.UUID) -> DashboardSummaryResponse:
    today = datetime.utcnow().date()
    seven_days_ago = today - timedelta(days=6)
    
    # 1. Fetch Mood for last 7 days
    moods = db.query(Mood).filter(
        Mood.user_id == user_id,
        Mood.record_date >= seven_days_ago,
        Mood.record_date <= today
    ).order_by(Mood.record_date.asc()).all()
    
    mood_dict = {m.record_date: m.mood_score for m in moods}
    
    ar_days_short = {0: "ن", 1: "ث", 2: "ر", 3: "خ", 4: "ج", 5: "س", 6: "ح"}
    ar_days_long = {0: "الاثنين", 1: "الثلاثاء", 2: "الأربعاء", 3: "الخميس", 4: "الجمعة", 5: "السبت", 6: "الأحد"}
    
    mood_chart = []
    for i in range(7):
        curr_date = seven_days_ago + timedelta(days=i)
        val = mood_dict.get(curr_date, 5) # default neutral
        mood_chart.append({
            "d": ar_days_short[curr_date.weekday()],
            "v": val
        })
        
    # 2. Fetch Digital Habits for last 7 days
    habits = db.query(DigitalHabits).filter(
        DigitalHabits.user_id == user_id,
        DigitalHabits.record_date >= seven_days_ago,
        DigitalHabits.record_date <= today
    ).order_by(DigitalHabits.record_date.asc()).all()
    
    habit_dict = {h.record_date: h.screen_time_minutes for h in habits}
    screen_time_chart = []
    total_screen = 0
    count_screen = 0
    for i in range(7):
        curr_date = seven_days_ago + timedelta(days=i)
        mins = habit_dict.get(curr_date, 0) # default 0 or maybe target
        hrs = round(mins / 60.0, 1) if mins > 0 else 0
        if hrs > 0:
            total_screen += hrs
            count_screen += 1
            
        screen_time_chart.append({
            "d": ar_days_long[curr_date.weekday()],
            "h": hrs if hrs > 0 else 4.0 # default 4.0 for empty days for visual
        })
        
    screen_time_avg = round(total_screen / count_screen, 1) if count_screen > 0 else 4.8
    
    # 3. Calculate Scores (Mocked calculation for now based on actual data)
    scores = [
        {"t": "الصحة الرقمية", "v": 82, "c": "text-primary", "i": "Activity", "to": "/digital-health"},
        {"t": "التعلّم", "v": 74, "c": "text-info", "i": "Brain", "to": "/learning-hub"},
        {"t": "الإنتاجية", "v": 68, "c": "text-warning", "i": "TrendingUp", "to": "/planner"},
        {"t": "الرفاه", "v": 79, "c": "text-success", "i": "Heart", "to": "/mood"}
    ]
    
    # 4. Smart Suggestions
    suggestions = [
        {"t": "جلسة تركيز قصيرة", "d": "لم تكمل أي جلسة بومودورو اليوم. ابدأ الآن لمدة ٢٥ دقيقة.", "a": "ابدأ الجلسة"},
        {"t": "استرخاء وتأمل", "d": "خصص ١٥ دقيقة للتأمل لرفع مستوى الرفاهية.", "a": "افتح التأمل"},
        {"t": "راجع أهدافك", "d": "لديك هدف لم تقم بتحديثه منذ يومين.", "a": "تحديث الأهداف"}
    ]
    
    return DashboardSummaryResponse(
        scores=scores,
        screen_time=screen_time_chart,
        screen_time_avg=screen_time_avg,
        mood_chart=mood_chart,
        suggestions=suggestions
    )
