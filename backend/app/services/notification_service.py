import uuid
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.notifications import Notifications
from app.schemas.notifications import NotificationCreate


async def get_user_notifications(
    db: AsyncSession, user_id: uuid.UUID, unread_only: bool = False
) -> List[Notifications]:
    stmt = select(Notifications).where(Notifications.user_id == user_id)
    if unread_only:
        stmt = stmt.where(Notifications.is_read == False)  # noqa: E712
    stmt = stmt.order_by(Notifications.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


async def create_notification(
    db: AsyncSession,
    user_id: str,
    message: str,
    notif_type: str = "system",
    title: str = "تنبيه",
) -> Notifications:
    db_notif = Notifications(user_id=user_id, title=title, message=message, notification_type=notif_type)
    db.add(db_notif)
    await db.commit()
    await db.refresh(db_notif)

    try:
        from app.services.websocket_manager import manager
        await manager.send_to_user(user_id, {
            "type": "notification",
            "id": db_notif.id,
            "message": db_notif.message,
            "notif_type": db_notif.notification_type,
            "is_read": db_notif.is_read,
            "created_at": db_notif.created_at.isoformat() if db_notif.created_at else None,
        })
    except Exception:
        pass

    return db_notif


async def create_notification_from_schema(
    db: AsyncSession, notification_in: NotificationCreate
) -> Notifications:
    db_notif = Notifications(**notification_in.model_dump())
    db.add(db_notif)
    await db.commit()
    await db.refresh(db_notif)
    return db_notif


async def mark_as_read(
    db: AsyncSession, user_id: str, notification_id: str
) -> Notifications:
    result = await db.execute(
        select(Notifications).where(
            Notifications.id == notification_id,
            Notifications.user_id == user_id,
        )
    )
    db_notif = result.scalars().first()
    if not db_notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    db_notif.is_read = True
    await db.commit()
    await db.refresh(db_notif)
    return db_notif


async def mark_all_as_read(db: AsyncSession, user_id: str) -> None:
    stmt = (
        update(Notifications)
        .where(
            Notifications.user_id == user_id,
            Notifications.is_read == False,  # noqa: E712
        )
        .values(is_read=True)
    )
    await db.execute(stmt)
    await db.commit()
