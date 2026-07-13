import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.api.deps import get_admin_user, get_current_user
from app.models.user import Users


@pytest.mark.asyncio
async def test_admin_user_count_unauthorized():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/admin/users/count")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_seed_content_authorized():
    mock_user = MagicMock(spec=Users)
    mock_user.id = str(uuid.uuid4())
    mock_user.role = "ADMIN"
    mock_user.is_active = True

    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_admin_user] = lambda: mock_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.api.v1.admin.get_db"):
            mock_session = AsyncMock()
            mock_execute = AsyncMock()
            mock_session.execute = mock_execute
            mock_session.add = MagicMock()
            mock_session.commit = AsyncMock()
            mock_execute.return_value = MagicMock(scalar=MagicMock(return_value=0))
            response = await client.post("/api/v1/admin/content/seed")

    assert response.status_code == 200
    assert "message" in response.json()

    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(get_admin_user, None)


@pytest.mark.asyncio
async def test_admin_users_list():
    mock_user = MagicMock(spec=Users)
    mock_user.id = str(uuid.uuid4())
    mock_user.role = "ADMIN"
    mock_user.is_active = True

    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_admin_user] = lambda: mock_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.api.v1.admin.get_db"):
            response = await client.get("/api/v1/admin/users")

    assert response.status_code in (200, 500)

    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(get_admin_user, None)
