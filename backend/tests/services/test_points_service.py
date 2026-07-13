import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.points_service import calculate_level, next_level_points, add_points, get_user_points_and_level


class TestCalculateLevel:
    def test_level_1_zero_points(self):
        assert calculate_level(0) == 1

    def test_level_2_at_threshold(self):
        assert calculate_level(100) == 2

    def test_level_3(self):
        assert calculate_level(250) == 3

    def test_level_4(self):
        assert calculate_level(500) == 4

    def test_level_5(self):
        assert calculate_level(1000) == 5

    def test_level_6(self):
        assert calculate_level(2000) == 6

    def test_level_7(self):
        assert calculate_level(3500) == 7

    def test_level_8_max(self):
        assert calculate_level(5000) == 8
        assert calculate_level(10000) == 8


class TestNextLevelPoints:
    def test_next_level_zero(self):
        assert next_level_points(0) == 100

    def test_next_level_between(self):
        assert next_level_points(150) == 250

    def test_next_level_max(self):
        assert next_level_points(10000) == 6000


@pytest.mark.asyncio
async def test_add_points_new():
    mock_db = AsyncMock()
    mock_profile = MagicMock()
    mock_profile.points = 0
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_profile
    mock_db.execute.return_value = mock_result

    with patch("app.services.points_service.create_notification", AsyncMock()):
        result = await add_points(mock_db, str(uuid.uuid4()), 50, "Test")

    assert result["added"] == 50
    assert result["points"] == 50
    assert mock_profile.points == 50


@pytest.mark.asyncio
async def test_add_points_level_up():
    mock_db = AsyncMock()
    mock_profile = MagicMock()
    mock_profile.points = 95
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_profile
    mock_db.execute.return_value = mock_result

    with patch("app.services.points_service.create_notification", AsyncMock()) as mock_notif:
        result = await add_points(mock_db, str(uuid.uuid4()), 10, "Test level up")

    assert result["added"] == 10
    assert result["points"] == 105
    assert result["level"] == 2


@pytest.mark.asyncio
async def test_get_user_points_and_level():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar.return_value = 500
    mock_db.execute = AsyncMock(return_value=mock_result)

    with patch("app.services.points_service.create_notification", AsyncMock()):
        result = await get_user_points_and_level(mock_db, str(uuid.uuid4()))

    assert result["points"] == 500
