import uuid
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.ml.classifier import _load_model as load_clf
from app.ml.risk_predictor import _load_model as load_risk
from app.ml.recommender import _load_vectorizer


class TestMLModelsLoaded:
    def test_classifier_model_loaded(self):
        model_data = load_clf()
        assert model_data is not None
        assert "model" in model_data
        assert "label_map" in model_data
        assert "reverse_map" in model_data
        assert model_data["accuracy"] > 0.8

    def test_risk_model_loaded(self):
        model_data = load_risk()
        assert model_data is not None
        assert "model" in model_data
        assert model_data["accuracy"] > 0.8

    def test_vectorizer_loaded(self):
        vec_data = _load_vectorizer()
        assert vec_data is not None
        assert "vectorizer" in vec_data


@pytest.mark.asyncio
async def test_classify_user_with_habits():
    mock_db = AsyncMock()
    user_id = str(uuid.uuid4())
    today = date.today()

    habit_mock = MagicMock()
    habit_mock.screen_time_minutes = 120
    habit_mock.social_media_minutes = 30
    habit_mock.sleep_minutes = 480
    habit_mock.record_date = today

    mood_mock = MagicMock()
    mood_mock.mood_score = 8
    mood_mock.stress_score = 3
    mood_mock.record_date = today

    task_mock = MagicMock()
    task_mock.is_completed = True
    goal_mock = MagicMock()
    goal_mock.status = "IN_PROGRESS"

    mock_habits_result = MagicMock()
    mock_habits_result.scalars.return_value.all.return_value = [habit_mock]
    mock_mood_result = MagicMock()
    mock_mood_result.scalars.return_value.all.return_value = [mood_mock]
    mock_tasks_result = MagicMock()
    mock_tasks_result.scalars.return_value.all.return_value = [task_mock]
    mock_goals_result = MagicMock()
    mock_goals_result.scalars.return_value.all.return_value = [goal_mock]

    mock_db.execute = AsyncMock(side_effect=[
        mock_habits_result, mock_mood_result,
        mock_tasks_result, mock_goals_result,
    ])

    from app.ml.classifier import classify_user
    result = await classify_user(mock_db, user_id)

    assert result.user_type in ("BALANCED", "HIGH_PERFORMER")
    assert 0 <= result.confidence <= 1.0


@pytest.mark.asyncio
async def test_classify_digital_addict():
    mock_db = AsyncMock()
    user_id = str(uuid.uuid4())
    today = date.today()

    habit_mock = MagicMock()
    habit_mock.screen_time_minutes = 600
    habit_mock.social_media_minutes = 400
    habit_mock.sleep_minutes = 240
    habit_mock.record_date = today

    mood_mock = MagicMock()
    mood_mock.mood_score = 2
    mood_mock.stress_score = 9
    mood_mock.record_date = today

    mock_habits_result = MagicMock()
    mock_habits_result.scalars.return_value.all.return_value = [habit_mock, habit_mock]
    mock_mood_result = MagicMock()
    mock_mood_result.scalars.return_value.all.return_value = [mood_mock, mood_mock]
    mock_empty = MagicMock()
    mock_empty.scalars.return_value.all.return_value = []

    mock_db.execute = AsyncMock(side_effect=[
        mock_habits_result, mock_mood_result,
        mock_empty, mock_empty,
    ])

    from app.ml.classifier import classify_user
    result = await classify_user(mock_db, user_id)

    assert result.user_type == "DIGITAL_ADDICT"
