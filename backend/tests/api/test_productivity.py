import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient, email: str = "prod@example.com") -> str:
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
async def test_create_goal(async_client: AsyncClient):
    token = await _register_and_login(async_client)
    response = await async_client.post(
        "/api/v1/productivity/goals",
        json={"title": "تعلم Python", "category": "تعليم"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "تعلم Python"
    assert data["status"] == "NOT_STARTED"


@pytest.mark.asyncio
async def test_get_goals(async_client: AsyncClient):
    token = await _register_and_login(async_client, "goals@example.com")
    await async_client.post(
        "/api/v1/productivity/goals",
        json={"title": "هدف ١"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = await async_client.get(
        "/api/v1/productivity/goals",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_create_task(async_client: AsyncClient):
    token = await _register_and_login(async_client, "task@example.com")
    response = await async_client.post(
        "/api/v1/productivity/tasks",
        json={"title": "مهمة اختبار"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "مهمة اختبار"
    assert data["is_completed"] is False


@pytest.mark.asyncio
async def test_complete_task(async_client: AsyncClient):
    token = await _register_and_login(async_client, "complete@example.com")
    create_resp = await async_client.post(
        "/api/v1/productivity/tasks",
        json={"title": "مهمة إنجاز"},
        headers={"Authorization": f"Bearer {token}"},
    )
    task_id = create_resp.json()["id"]
    response = await async_client.put(
        f"/api/v1/productivity/tasks/{task_id}",
        json={"is_completed": True, "status": "DONE"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["is_completed"] is True


@pytest.mark.asyncio
async def test_planner_crud(async_client: AsyncClient):
    token = await _register_and_login(async_client, "planner@example.com")
    create_resp = await async_client.post(
        "/api/v1/productivity/planner",
        json={
            "title": "اجتماع فريق",
            "plan_date": "2026-07-15",
            "start_time": "10:00:00",
            "end_time": "11:00:00",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_resp.status_code == 200
    item_id = create_resp.json()["id"]

    get_resp = await async_client.get(
        "/api/v1/productivity/planner",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 200

    delete_resp = await async_client.delete(
        f"/api/v1/productivity/planner/{item_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_resp.status_code == 200
