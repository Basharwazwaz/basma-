import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "StrongPass1",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data
    assert data["is_active"] is True

@pytest.mark.asyncio
async def test_register_duplicate_email(async_client: AsyncClient):
    payload = {
        "email": "dup@example.com",
        "password": "StrongPass1",
    }
    await async_client.post("/api/v1/auth/register", json=payload)
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_login_user(async_client: AsyncClient):
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "loginuser@example.com",
            "password": "LoginPass1",
            "first_name": "Login",
            "last_name": "User"
        }
    )
    response = await async_client.post(
        "/api/v1/auth/login",
        data={
            "username": "loginuser@example.com",
            "password": "LoginPass1"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_password(async_client: AsyncClient):
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "wrong@example.com", "password": "CorrectPass1"}
    )
    response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "wrong@example.com", "password": "WrongPass1"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_login_nonexistent_user(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "nobody@example.com", "password": "pass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_protected_route_no_token(async_client: AsyncClient):
    response = await async_client.get("/api/v1/user/me")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_protected_route_valid_token(async_client: AsyncClient):
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "token@example.com", "password": "TokenPass1"}
    )
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "token@example.com", "password": "TokenPass1"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = login_resp.json()["access_token"]
    response = await async_client.get(
        "/api/v1/user/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "token@example.com"
