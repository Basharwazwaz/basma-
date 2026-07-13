import uuid
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import Users
from app.schemas.gamification import (
    ChallengeResponse,
    UserChallengeCreate,
    UserChallengeUpdate,
    UserChallengeResponse,
    AchievementResponse,
)
from app.services import gamification_service

router = APIRouter()


# ---------------------------------------------------------------------------
# Challenges
# ---------------------------------------------------------------------------

@router.get("/challenges", response_model=List[ChallengeResponse])
async def get_all_challenges(db: AsyncSession = Depends(get_db)):
    """Get all available challenges in the platform."""
    return await gamification_service.get_all_challenges(db)


@router.get("/challenges/user", response_model=List[UserChallengeResponse])
async def get_user_challenges(
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Get challenges the current user is enrolled in."""
    return await gamification_service.get_user_challenges(db, current_user.id)


@router.post("/challenges/enroll", response_model=UserChallengeResponse)
async def enroll_in_challenge(
    enroll_in: UserChallengeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Enroll the user in a new challenge."""
    return await gamification_service.enroll_user_in_challenge(
        db, current_user.id, enroll_in.challenge_id
    )


@router.put("/challenges/{user_challenge_id}", response_model=UserChallengeResponse)
async def update_challenge_progress(
    user_challenge_id: str,
    update_in: UserChallengeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Update progress or status of an enrolled challenge."""
    return await gamification_service.update_user_challenge(
        db, current_user.id, user_challenge_id, update_in
    )


@router.post("/challenges/{user_challenge_id}/checkin", response_model=UserChallengeResponse)
async def checkin_challenge(
    user_challenge_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Daily check-in for an enrolled challenge. Increments progress by 1."""
    return await gamification_service.checkin_user_challenge(
        db, current_user.id, user_challenge_id
    )


# ---------------------------------------------------------------------------
# Achievements
# ---------------------------------------------------------------------------

@router.get("/achievements", response_model=List[AchievementResponse])
async def get_achievements(
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Get user's earned achievements."""
    return await gamification_service.get_user_achievements(db, current_user.id)
