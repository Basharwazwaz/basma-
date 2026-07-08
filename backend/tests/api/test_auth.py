import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "strongpassword123",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data

@pytest.mark.asyncio
async def test_login_user(async_client: AsyncClient):
    # Register first
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "loginuser@example.com",
            "password": "loginpassword123",
            "first_name": "Login",
            "last_name": "User"
        }
    )
    
    # Then login
    response = await async_client.post(
        "/api/v1/auth/login",
        data={
            "username": "loginuser@example.com",
            "password": "loginpassword123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
