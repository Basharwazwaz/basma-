import uuid
from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.health import Mood, DigitalHabits
from app.schemas.health import MoodCreate, MoodUpdate, DigitalHabitsCreate, DigitalHabitsUpdate

# --- Mood Service ---

def get_moods(db: Session, user_id: uuid.UUID, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Mood]:
    query = db.query(Mood).filter(Mood.user_id == user_id)
    if start_date:
        query = query.filter(Mood.record_date >= start_date)
    if end_date:
        query = query.filter(Mood.record_date <= end_date)
    return query.order_by(Mood.record_date.desc()).all()

def get_mood_by_date(db: Session, user_id: uuid.UUID, record_date: date) -> Optional[Mood]:
    return db.query(Mood).filter(Mood.user_id == user_id, Mood.record_date == record_date).first()

def create_or_update_mood(db: Session, user_id: uuid.UUID, mood_in: MoodCreate) -> Mood:
    db_mood = get_mood_by_date(db, user_id, mood_in.record_date)
    
    if db_mood:
        # Update
        update_data = mood_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_mood, field, value)
    else:
        # Create
        db_mood = Mood(user_id=user_id, **mood_in.model_dump())
        db.add(db_mood)
        
    db.commit()
    db.refresh(db_mood)
    return db_mood

def delete_mood(db: Session, user_id: uuid.UUID, mood_id: uuid.UUID):
    db_mood = db.query(Mood).filter(Mood.id == mood_id, Mood.user_id == user_id).first()
    if not db_mood:
        raise HTTPException(status_code=404, detail="Mood record not found")
    db.delete(db_mood)
    db.commit()

# --- Digital Habits Service ---

def get_digital_habits(db: Session, user_id: uuid.UUID, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[DigitalHabits]:
    query = db.query(DigitalHabits).filter(DigitalHabits.user_id == user_id)
    if start_date:
        query = query.filter(DigitalHabits.record_date >= start_date)
    if end_date:
        query = query.filter(DigitalHabits.record_date <= end_date)
    return query.order_by(DigitalHabits.record_date.desc()).all()

def get_digital_habits_by_date(db: Session, user_id: uuid.UUID, record_date: date) -> Optional[DigitalHabits]:
    return db.query(DigitalHabits).filter(DigitalHabits.user_id == user_id, DigitalHabits.record_date == record_date).first()

def create_or_update_digital_habits(db: Session, user_id: uuid.UUID, habits_in: DigitalHabitsCreate) -> DigitalHabits:
    db_habits = get_digital_habits_by_date(db, user_id, habits_in.record_date)
    
    if db_habits:
        update_data = habits_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_habits, field, value)
    else:
        db_habits = DigitalHabits(user_id=user_id, **habits_in.model_dump())
        db.add(db_habits)
        
    db.commit()
    db.refresh(db_habits)
    return db_habits
