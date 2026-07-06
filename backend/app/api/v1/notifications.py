from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import Users
from app.schemas.notifications import NotificationResponse
from app.services import notification_service

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
def get_notifications(
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Get user notifications."""
    return notification_service.get_user_notifications(db, current_user.id, unread_only)

@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Mark a single notification as read."""
    return notification_service.mark_as_read(db, current_user.id, notification_id)

@router.put("/read-all")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Mark all unread notifications as read."""
    notification_service.mark_all_as_read(db, current_user.id)
    return {"status": "success"}
