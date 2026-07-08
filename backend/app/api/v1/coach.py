from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.schemas.coach import MessageCreate, MessageResponse
from app.services import coach_service
from app.models.user import Users

router = APIRouter()

@router.get("/messages", response_model=List[MessageResponse])
async def get_messages(
    db: AsyncSession = Depends(deps.get_db),
    current_user: Users = Depends(deps.get_current_user),
):
    """
    Get all chat messages for the current user.
    """
    messages = await coach_service.get_chat_history(db, current_user.id)
    return messages


@router.post("/chat", response_model=MessageResponse)
async def chat_with_coach(
    message_in: MessageCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Users = Depends(deps.get_current_user),
):
    """
    Send a message to the AI coach and get a response.
    Returns the AI's response message.
    """
    return await coach_service.chat_with_coach(db, current_user.id, message_in)


@router.delete("/messages", status_code=status.HTTP_204_NO_CONTENT)
async def clear_messages(
    db: AsyncSession = Depends(deps.get_db),
    current_user: Users = Depends(deps.get_current_user),
):
    """
    Clear all chat messages for the current user.
    """
    await coach_service.clear_chat_history(db, current_user.id)
    return None
