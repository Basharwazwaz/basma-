import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient, email: str, password: str = "TestPass1") -> str:
    """Helper: register a user and return the access token."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "first_name": "Test", "last_name": "User"},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return resp.json()["access_token"]


# ── Refresh Token ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_refresh_token_success(async_client: AsyncClient):
    email = "refresh_ok@example.com"
    password = "RefreshPass1"
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_resp.status_code == 200
    refresh_cookie = login_resp.cookies.get("refresh_token")
    assert refresh_cookie is not None

    response = await async_client.post(
        "/api/v1/auth/refresh",
        cookies={"refresh_token": refresh_cookie},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_token_missing(async_client: AsyncClient):
    response = await async_client.post("/api/v1/auth/refresh")
    assert response.status_code == 401


# ── Logout ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_logout_revokes_refresh_token(async_client: AsyncClient):
    email = "logout_ok@example.com"
    password = "LogoutPass1"
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    refresh_cookie = login_resp.cookies.get("refresh_token")
    access_token = login_resp.json()["access_token"]
    assert refresh_cookie is not None

    # Logout
    logout_resp = await async_client.post(
        "/api/v1/auth/logout",
        cookies={"refresh_token": refresh_cookie},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert logout_resp.status_code == 200

    # Refresh should now fail
    refresh_resp = await async_client.post(
        "/api/v1/auth/refresh",
        cookies={"refresh_token": refresh_cookie},
    )
    assert refresh_resp.status_code == 401


# ── Daily Mood Upsert ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_daily_mood_upsert(async_client: AsyncClient):
    token = await _register_and_login(async_client, "mood_upsert@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "mood_score": 7,
        "stress_score": 3,
        "mood_state": "GOOD",
        "record_date": "2026-07-11",
    }
    resp1 = await async_client.post("/api/v1/health/mood", json=payload, headers=headers)
    assert resp1.status_code == 200

    # Same date should upsert (update), not fail
    payload["mood_score"] = 9
    resp2 = await async_client.post("/api/v1/health/mood", json=payload, headers=headers)
    assert resp2.status_code == 200
    assert resp2.json()["mood_score"] == 9


# ── Gamification Checkin ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_gamification_challenge_list(async_client: AsyncClient):
    token = await _register_and_login(async_client, "gamif_list@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await async_client.get("/api/v1/gamification/challenges", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_gamification_achievements_empty(async_client: AsyncClient):
    token = await _register_and_login(async_client, "gamif_ach@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await async_client.get("/api/v1/gamification/achievements", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


# ── Content Endpoints ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_content_list(async_client: AsyncClient):
    token = await _register_and_login(async_client, "content_list@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await async_client.get("/api/v1/content/", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
