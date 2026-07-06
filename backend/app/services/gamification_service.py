import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.gamification import Challenges, UserChallenges, Achievements
from app.schemas.gamification import UserChallengeCreate, UserChallengeUpdate

# --- Challenges ---

def get_all_challenges(db: Session) -> List[Challenges]:
    """Returns all available platform challenges."""
    return db.query(Challenges).all()

def get_user_challenges(db: Session, user_id: uuid.UUID) -> List[UserChallenges]:
    """Returns challenges enrolled by the user."""
    return db.query(UserChallenges).filter(UserChallenges.user_id == user_id).all()

def enroll_user_in_challenge(db: Session, user_id: uuid.UUID, challenge_id: uuid.UUID) -> UserChallenges:
    # Check if challenge exists
    challenge = db.query(Challenges).filter(Challenges.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
        
    # Check if already enrolled
    existing = db.query(UserChallenges).filter(
        UserChallenges.user_id == user_id, 
        UserChallenges.challenge_id == challenge_id
    ).first()
    
    if existing:
        return existing
        
    new_enrollment = UserChallenges(
        user_id=user_id,
        challenge_id=challenge_id,
        status="ACTIVE",
        progress_days=0
    )
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)
    return new_enrollment

def update_user_challenge(db: Session, user_id: uuid.UUID, user_challenge_id: uuid.UUID, update_in: UserChallengeUpdate) -> UserChallenges:
    db_uchallenge = db.query(UserChallenges).filter(
        UserChallenges.id == user_challenge_id,
        UserChallenges.user_id == user_id
    ).first()
    
    if not db_uchallenge:
        raise HTTPException(status_code=404, detail="User challenge not found")
        
    update_data = update_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_uchallenge, field, value)
        
    db.commit()
    db.refresh(db_uchallenge)
    return db_uchallenge

# --- Achievements ---

def get_user_achievements(db: Session, user_id: uuid.UUID) -> List[Achievements]:
    return db.query(Achievements).filter(Achievements.user_id == user_id).all()

def award_achievement(db: Session, user_id: uuid.UUID, title: str, description: Optional[str] = None, icon: Optional[str] = None) -> Achievements:
    existing = db.query(Achievements).filter(
        Achievements.user_id == user_id,
        Achievements.title == title
    ).first()
    
    if existing:
        return existing
        
    achievement = Achievements(
        user_id=user_id,
        title=title,
        description=description,
        icon=icon
    )
    db.add(achievement)
    db.commit()
    db.refresh(achievement)
    return achievement
