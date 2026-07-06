# Import all the models here so Alembic can discover them.
# The actual models will be imported here after they are created.

from app.db.base_class import Base

# Import all models here for Alembic
from app.models.user import Users, Profiles
from app.models.auth import RefreshTokens
from app.models.health import Mood, DigitalHabits
from app.models.productivity import Goals, Tasks, Planner
from app.models.gamification import Challenges, UserChallenges, Achievements
from app.models.content import LearningContent, Recommendations
from app.models.analytics import WeeklyReports, AIInsights
from app.models.notifications import Notifications
