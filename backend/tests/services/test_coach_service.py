import uuid
import pytest
from app.services.coach_service import chat_with_coach, get_chat_history
from app.schemas.coach import MessageCreate
from app.models.user import Users

@pytest.mark.asyncio
async def test_chat_fallback(test_db_session):
    # Create a mock user first
    user_id = uuid.uuid4()
    mock_user = Users(
        id=user_id,
        email="coachuser@example.com",
        hashed_password="mock",
        is_active=True,
    )
    test_db_session.add(mock_user)
    await test_db_session.commit()
    
    # Test chat
    msg = MessageCreate(content="مرحبا")
    response = await chat_with_coach(test_db_session, user_id, msg)
    
    assert response is not None
    assert response.role == "ai"
    assert "مفتاح" in response.content or "المطور" in response.content
    
    # Check history
    history = await get_chat_history(test_db_session, user_id)
    assert len(history) == 2
    assert history[0].role == "user"
    assert history[0].content == "مرحبا"
    assert history[1].role == "ai"
