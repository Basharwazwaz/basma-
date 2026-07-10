import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient, email: str = "profile@example.com") -> str:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "TestPass1", "first_name": "أحمد"},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "TestPass1"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_get_profile(async_client: AsyncClient):
    token = await _register_and_login(async_client)
    response = await async_client.get(
        "/api/v1/profile/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "profile@example.com"
    assert data["profile"] is not None


@pytest.mark.asyncio
async def test_update_profile(async_client: AsyncClient):
    token = await _register_and_login(async_client, "update@example.com")
    response = await async_client.put(
        "/api/v1/profile/",
        json={"first_name": "محمد", "city": "الرياض"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "محمد"
    assert data["city"] == "الرياض"


@pytest.mark.asyncio
async def test_update_settings(async_client: AsyncClient):
    token = await _register_and_login(async_client, "settings@example.com")
    response = await async_client.put(
        "/api/v1/profile/settings",
        json={"theme": "dark", "language": "en"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["theme"] == "dark"
    assert data["language"] == "en"


@pytest.mark.asyncio
async def test_onboarding(async_client: AsyncClient):
    token = await _register_and_login(async_client, "onboard@example.com")
    response = await async_client.post(
        "/api/v1/profile/onboarding",
        json={
            "personal": {"age": 22, "city": "جدة"},
            "digital": {
                "screen_time_hours": 5,
                "social_media_hours": 2,
                "sleep_hours": 7,
            },
            "mental": {
                "mood_score": 8,
                "stress_score": 4,
                "mood_state": "GOOD",
            },
            "plan": {
                "goals": ["تعلم البرمجة"],
                "interests": ["تقنية"],
            },
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_delete_account(async_client: AsyncClient):
    token = await _register_and_login(async_client, "delete@example.com")
    response = await async_client.delete(
        "/api/v1/profile/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204
