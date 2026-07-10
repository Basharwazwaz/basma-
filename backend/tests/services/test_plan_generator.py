import uuid
from datetime import date, time
from unittest.mock import AsyncMock, MagicMock
import pytest
from app.services.plan_generator import generate_study_plan, _distribute_tasks


class MockTask:
    def __init__(self, title="Test Task", due_date=None, is_completed=False):
        self.id = uuid.uuid4()
        self.title = title
        self.due_date = due_date
        self.is_completed = is_completed


def test_distribute_tasks_basic():
    """Test basic task distribution across a week."""
    tasks = [
        MockTask("Task 1", due_date=date(2026, 7, 14)),
        MockTask("Task 2", due_date=date(2026, 7, 15)),
        MockTask("Task 3", due_date=date(2026, 7, 16)),
    ]
    week_start = date(2026, 7, 13)  # Monday

    distribution = _distribute_tasks(tasks, week_start, 180)

    assert len(distribution) > 0
    total_assigned = sum(len(v) for v in distribution.values())
    assert total_assigned == 3


def test_distribute_tasks_empty():
    """Test distribution with no tasks."""
    distribution = _distribute_tasks([], date(2026, 7, 13), 180)
    assert len(distribution) == 0


@pytest.mark.asyncio
async def test_generate_study_plan_no_data():
    """Test plan generation with no pending tasks."""
    mock_db = AsyncMock()

    # Mock empty results for goals, tasks, habits
    empty_result = MagicMock()
    empty_result.scalars.return_value.all.return_value = []

    mock_db.execute.side_effect = [empty_result, empty_result, empty_result]

    events = await generate_study_plan(mock_db, uuid.uuid4())

    # Should still generate at least some review sessions
    assert len(events) >= 1
    assert all(e.event_type in ("study", "break", "review", "health") for e in events)
