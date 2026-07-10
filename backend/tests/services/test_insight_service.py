import uuid
from datetime import date
from unittest.mock import AsyncMock, MagicMock
import pytest
from app.services.insight_service import generate_insights, Insight


@pytest.mark.asyncio
async def test_generate_insights_no_data():
    """Test insights generation with no data returns a TIP."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    insights = await generate_insights(mock_db, uuid.uuid4())

    assert len(insights) >= 1
    assert insights[0].insight_type == "TIP"
    assert "بياناتك" in insights[0].message or "سجّل" in insights[0].message


@pytest.mark.asyncio
async def test_generate_insights_with_habits():
    """Test insights generation with habit data."""
    mock_db = AsyncMock()

    # Create mock habits
    mock_habit = MagicMock()
    mock_habit.screen_time_minutes = 600  # 10 hours
    mock_habit.social_media_minutes = 400
    mock_habit.sleep_minutes = 360  # 6 hours
    mock_habit.record_date = date.today()

    mock_mood = MagicMock()
    mock_mood.mood_score = 4
    mock_mood.stress_score = 8
    mock_mood.record_date = date.today()

    mock_task = MagicMock()
    mock_task.is_completed = False

    # Mock results for habits, moods, tasks
    result1 = MagicMock()
    result1.scalars.return_value.all.return_value = [mock_habit]

    result2 = MagicMock()
    result2.scalars.return_value.all.return_value = [mock_mood]

    result3 = MagicMock()
    result3.scalars.return_value.all.return_value = [mock_task]

    mock_db.execute.side_effect = [result1, result2, result3]

    insights = await generate_insights(mock_db, uuid.uuid4())

    assert len(insights) > 0
    # Should detect high screen time and poor sleep
    types = [i.insight_type for i in insights]
    assert "WARNING" in types or "TIP" in types
