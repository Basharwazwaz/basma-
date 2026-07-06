from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import date

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import Users
from app.schemas.health import (
    MoodCreate, MoodUpdate, MoodResponse,
    DigitalHabitsCreate, DigitalHabitsUpdate, DigitalHabitsResponse
)
from app.services import health_service

router = APIRouter()

# --- Mood ---

@router.get("/mood", response_model=List[MoodResponse])
def get_moods(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    return health_service.get_moods(db, current_user.id, start_date, end_date)

@router.post("/mood", response_model=MoodResponse)
def log_mood(
    mood_in: MoodCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    return health_service.create_or_update_mood(db, current_user.id, mood_in)

@router.delete("/mood/{mood_id}")
def delete_mood(
    mood_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    health_service.delete_mood(db, current_user.id, mood_id)
    return {"status": "success"}

# --- Digital Habits ---

@router.get("/habits", response_model=List[DigitalHabitsResponse])
def get_digital_habits(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    return health_service.get_digital_habits(db, current_user.id, start_date, end_date)

@router.post("/habits", response_model=DigitalHabitsResponse)
def log_digital_habits(
    habits_in: DigitalHabitsCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    return health_service.create_or_update_digital_habits(db, current_user.id, habits_in)
