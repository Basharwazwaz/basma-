"""
Points and Levels Service
Manages user points, level calculation, and awards points for various actions.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import Profiles
from app.services.notification_service import create_notification

LEVEL_THRESHOLDS = [
    (1, 0),
    (2, 100),
    (3, 250),
    (4, 500),
    (5, 1000),
    (6, 2000),
    (7, 3500),
    (8, 5000),
]


def calculate_level(points: int) -> int:
    level = 1
    for lvl, threshold in reversed(LEVEL_THRESHOLDS):
        if points >= threshold:
            level = lvl
            break
    return level


def next_level_points(points: int) -> int:
    for lvl, threshold in LEVEL_THRESHOLDS:
        if points < threshold:
            return threshold
    return LEVEL_THRESHOLDS[-1][1] + 1000


async def add_points(
    db: AsyncSession,
    user_id: str,
    points: int,
    reason: str,
) -> dict:
    result = await db.execute(
        select(Profiles).where(Profiles.user_id == user_id)
    )
    profile = result.scalars().first()
    if not profile:
        return {"points": 0, "level": 1, "added": 0}

    old_level = calculate_level(profile.points)
    profile.points += points
    new_level = calculate_level(profile.points)

    await db.commit()

    if new_level > old_level:
        await create_notification(
            db, user_id,
            message=f"تهانينا! لقد وصلت إلى المستوى {new_level}! 🎉",
            notif_type="achievement",
        )

    await create_notification(
        db, user_id,
        message=f"+{points} نقطة: {reason}",
        notif_type="points",
    )

    return {
        "points": profile.points,
        "level": new_level,
        "added": points,
    }


async def get_user_points_and_level(db: AsyncSession, user_id: str) -> dict:
    result = await db.execute(
        select(Profiles.points).where(Profiles.user_id == user_id)
    )
    points = result.scalar() or 0
    level = calculate_level(points)
    next_level = next_level_points(points)

    return {
        "points": points,
        "level": level,
        "next_level_points": next_level,
        "points_to_next_level": max(0, next_level - points),
    }
