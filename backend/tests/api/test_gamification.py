import pytest
from httpx import AsyncClient
from app.models.gamification import Challenges


async def _register_and_login(client: AsyncClient, email: str = "gamif@example.com") -> str:
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


async def _seed_challenge(session) -> str:
    ch = Challenges(
        title="Test Challenge",
        description="desc",
        category="general",
        duration_days=7,
        points_reward=50,
    )
    session.add(ch)
    await session.commit()
    await session.refresh(ch)
    return str(ch.id)


@pytest.mark.asyncio
async def test_get_all_challenges(async_client: AsyncClient):
    response = await async_client.get("/api/v1/gamification/challenges")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_enroll_and_checkin_challenge(async_client: AsyncClient, test_db_session):
    token = await _register_and_login(async_client, "checkin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    ch_id = await _seed_challenge(test_db_session)

    # Enroll
    resp = await async_client.post(
        "/api/v1/gamification/challenges/enroll",
        json={"challenge_id": ch_id},
        headers=headers,
    )
    assert resp.status_code == 200
    uc = resp.json()
    uc_id = uc["id"]
    assert uc["progress_days"] == 0

    # Check-in
    resp = await async_client.post(
        f"/api/v1/gamification/challenges/{uc_id}/checkin",
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["progress_days"] == 1
    assert resp.json()["last_checkin"] is not None

    # Duplicate check-in same day should fail
    resp = await async_client.post(
        f"/api/v1/gamification/challenges/{uc_id}/checkin",
        headers=headers,
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_get_user_achievements(async_client: AsyncClient):
    token = await _register_and_login(async_client)
    response = await async_client.get(
        "/api/v1/gamification/achievements",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_notifications(async_client: AsyncClient):
    token = await _register_and_login(async_client, "notif@example.com")
    response = await async_client.get(
        "/api/v1/notifications/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_dashboard_summary(async_client: AsyncClient):
    token = await _register_and_login(async_client, "dash@example.com")
    response = await async_client.get(
        "/api/v1/dashboard/summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "scores" in data
    assert "suggestions" in data
    assert "mood_chart" in data


@pytest.mark.asyncio
async def test_weekly_reports(async_client: AsyncClient):
    token = await _register_and_login(async_client, "weekly@example.com")
    response = await async_client.get(
        "/api/v1/weekly-reports/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
