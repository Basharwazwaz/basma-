import uuid
from typing import List

from fastapi import HTTPException
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
    db: AsyncSession, notification_in: NotificationCreate
) -> Notifications:
    db_notif = Notifications(**notification_in.model_dump())
    db.add(db_notif)
    await db.commit()
    await db.refresh(db_notif)
    return db_notif


async def mark_as_read(
    db: AsyncSession, user_id: uuid.UUID, notification_id: uuid.UUID
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


async def mark_all_as_read(db: AsyncSession, user_id: uuid.UUID) -> None:
    result = await db.execute(
        select(Notifications).where(
            Notifications.user_id == user_id,
            Notifications.is_read == False,  # noqa: E712
        )
    )
    for notif in result.scalars().all():
        notif.is_read = True
    await db.commit()
