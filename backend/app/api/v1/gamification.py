from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import Users
from app.schemas.gamification import (
    ChallengeResponse, UserChallengeCreate, UserChallengeUpdate, UserChallengeResponse,
    AchievementResponse
)
from app.services import gamification_service

router = APIRouter()

# --- Challenges ---

@router.get("/challenges", response_model=List[ChallengeResponse])
def get_all_challenges(db: Session = Depends(get_db)):
    """Get all available challenges in the platform."""
    return gamification_service.get_all_challenges(db)

@router.get("/challenges/user", response_model=List[UserChallengeResponse])
def get_user_challenges(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Get challenges the current user is enrolled in."""
    return gamification_service.get_user_challenges(db, current_user.id)

@router.post("/challenges/enroll", response_model=UserChallengeResponse)
def enroll_in_challenge(
    enroll_in: UserChallengeCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Enroll the user in a new challenge."""
    return gamification_service.enroll_user_in_challenge(db, current_user.id, enroll_in.challenge_id)

@router.put("/challenges/{user_challenge_id}", response_model=UserChallengeResponse)
def update_challenge_progress(
    user_challenge_id: uuid.UUID,
    update_in: UserChallengeUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Update progress or status of an enrolled challenge."""
    return gamification_service.update_user_challenge(db, current_user.id, user_challenge_id, update_in)

# --- Achievements ---

@router.get("/achievements", response_model=List[AchievementResponse])
def get_achievements(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Get user's earned achievements."""
    return gamification_service.get_user_achievements(db, current_user.id)
