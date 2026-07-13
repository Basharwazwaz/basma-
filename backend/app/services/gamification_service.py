import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.gamification import Challenges, UserChallenges, Achievements
from app.schemas.gamification import UserChallengeUpdate


# ---------------------------------------------------------------------------
# Challenges
# ---------------------------------------------------------------------------

async def get_all_challenges(db: AsyncSession) -> List[Challenges]:
    """Returns all available platform challenges."""
    result = await db.execute(select(Challenges))
    return result.scalars().all()


async def get_user_challenges(
    db: AsyncSession, user_id: uuid.UUID
) -> List[UserChallenges]:
    """Returns challenges enrolled by the user."""
    result = await db.execute(
        select(UserChallenges).where(UserChallenges.user_id == user_id)
    )
    return result.scalars().all()


async def enroll_user_in_challenge(
    db: AsyncSession, user_id: uuid.UUID, challenge_id: uuid.UUID
) -> UserChallenges:
    # Check challenge exists
    ch_result = await db.execute(
        select(Challenges).where(Challenges.id == challenge_id)
    )
    challenge = ch_result.scalars().first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    # Check already enrolled
    ex_result = await db.execute(
        select(UserChallenges).where(
            UserChallenges.user_id == user_id,
            UserChallenges.challenge_id == challenge_id,
        )
    )
    existing = ex_result.scalars().first()
    if existing:
        return existing

    new_enrollment = UserChallenges(
        user_id=user_id,
        challenge_id=challenge_id,
        status="ACTIVE",
        progress_days=0,
    )
    db.add(new_enrollment)
    await db.commit()
    await db.refresh(new_enrollment, ["challenge"])
    return new_enrollment


async def update_user_challenge(
    db: AsyncSession,
    user_id: uuid.UUID,
    user_challenge_id: uuid.UUID,
    update_in: UserChallengeUpdate,
) -> UserChallenges:
    result = await db.execute(
        select(UserChallenges).where(
            UserChallenges.id == user_challenge_id,
            UserChallenges.user_id == user_id,
        )
    )
    db_uchallenge = result.scalars().first()
    if not db_uchallenge:
        raise HTTPException(status_code=404, detail="User challenge not found")

    for field, value in update_in.model_dump(exclude_unset=True).items():
        setattr(db_uchallenge, field, value)

    await db.commit()
    await db.refresh(db_uchallenge, ["challenge"])
    return db_uchallenge


async def checkin_user_challenge(
    db: AsyncSession,
    user_id: uuid.UUID,
    user_challenge_id: uuid.UUID,
) -> UserChallenges:
    """Daily check-in: increment progress_days by 1, enforcing 1 check-in per day."""
    result = await db.execute(
        select(UserChallenges).where(
            UserChallenges.id == user_challenge_id,
            UserChallenges.user_id == user_id,
        )
    )
    db_uchallenge = result.scalars().first()
    if not db_uchallenge:
        raise HTTPException(status_code=404, detail="User challenge not found")

    if db_uchallenge.status != "ACTIVE":
        raise HTTPException(status_code=400, detail="Challenge is not active")

    now = datetime.now(timezone.utc)
    if db_uchallenge.last_checkin:
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        last = db_uchallenge.last_checkin
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        if last >= today_start:
            raise HTTPException(status_code=400, detail="Already checked in today")

    db_uchallenge.progress_days += 1
    db_uchallenge.last_checkin = now

    # Auto-complete if progress reaches duration
    ch_result = await db.execute(
        select(Challenges).where(Challenges.id == db_uchallenge.challenge_id)
    )
    challenge = ch_result.scalars().first()
    if challenge and db_uchallenge.progress_days >= challenge.duration_days:
        db_uchallenge.status = "COMPLETED"
        db_uchallenge.completed_at = now
        from app.services.points_service import add_points
        await add_points(db, user_id, 50, f"إكمال التحدي: {challenge.title}")

    from app.services.points_service import add_points
    await add_points(db, user_id, 5, "تسجيل حضور يومي في التحدي")

    await db.commit()
    await db.refresh(db_uchallenge, ["challenge"])
    return db_uchallenge
# ---------------------------------------------------------------------------

async def get_user_achievements(
    db: AsyncSession, user_id: uuid.UUID
) -> List[Achievements]:
    result = await db.execute(
        select(Achievements).where(Achievements.user_id == user_id)
    )
    return result.scalars().all()


async def award_achievement(
    db: AsyncSession,
    user_id: uuid.UUID,
    title: str,
    description: Optional[str] = None,
    icon: Optional[str] = None,
) -> Achievements:
    ex_result = await db.execute(
        select(Achievements).where(
            Achievements.user_id == user_id,
            Achievements.title == title,
        )
    )
    existing = ex_result.scalars().first()
    if existing:
        return existing

    achievement = Achievements(
        user_id=user_id,
        title=title,
        description=description,
        icon=icon,
    )
    db.add(achievement)
    from app.services.points_service import add_points
    await add_points(db, user_id, 15, f"الحصول على وسام: {title}")

    await db.commit()
    await db.refresh(achievement)
    return achievement
