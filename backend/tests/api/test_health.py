import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient, email: str = "health@example.com") -> str:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "TestPass1"},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "TestPass1"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_log_mood(async_client: AsyncClient):
    token = await _register_and_login(async_client)
    response = await async_client.post(
        "/api/v1/health/mood",
        json={
            "mood_score": 8,
            "stress_score": 3,
            "mood_state": "GOOD",
            "record_date": "2026-07-10",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mood_score"] == 8
    assert data["mood_state"] == "GOOD"


@pytest.mark.asyncio
async def test_get_moods(async_client: AsyncClient):
    token = await _register_and_login(async_client, "moods@example.com")
    await async_client.post(
        "/api/v1/health/mood",
        json={
            "mood_score": 7,
            "stress_score": 4,
            "mood_state": "NEUTRAL",
            "record_date": "2026-07-09",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    response = await async_client.get(
        "/api/v1/health/mood",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_log_digital_habits(async_client: AsyncClient):
    token = await _register_and_login(async_client, "habits@example.com")
    response = await async_client.post(
        "/api/v1/health/habits",
        json={
            "screen_time_minutes": 240,
            "social_media_minutes": 120,
            "sleep_minutes": 480,
            "record_date": "2026-07-10",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["screen_time_minutes"] == 240


@pytest.mark.asyncio
async def test_get_digital_health_analytics(async_client: AsyncClient):
    token = await _register_and_login(async_client, "analytics@example.com")
    response = await async_client.get(
        "/api/v1/health/analytics?days=7",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "health_score" in data
    assert "screen_time_chart" in data
