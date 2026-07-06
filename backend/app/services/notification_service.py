import uuid
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.notifications import Notifications
from app.schemas.notifications import NotificationCreate

def get_user_notifications(db: Session, user_id: uuid.UUID, unread_only: bool = False) -> List[Notifications]:
    query = db.query(Notifications).filter(Notifications.user_id == user_id)
    if unread_only:
        query = query.filter(Notifications.is_read == False)
    return query.order_by(Notifications.created_at.desc()).all()

def create_notification(db: Session, notification_in: NotificationCreate) -> Notifications:
    db_notif = Notifications(**notification_in.model_dump())
    db.add(db_notif)
    db.commit()
    db.refresh(db_notif)
    return db_notif

def mark_as_read(db: Session, user_id: uuid.UUID, notification_id: uuid.UUID) -> Notifications:
    db_notif = db.query(Notifications).filter(
        Notifications.id == notification_id,
        Notifications.user_id == user_id
    ).first()
    
    if not db_notif:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    db_notif.is_read = True
    db.commit()
    db.refresh(db_notif)
    return db_notif

def mark_all_as_read(db: Session, user_id: uuid.UUID):
    db.query(Notifications).filter(
        Notifications.user_id == user_id,
        Notifications.is_read == False
    ).update({"is_read": True})
    db.commit()
