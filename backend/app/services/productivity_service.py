import uuid
from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.productivity import Goals, Tasks, Planner, GoalStatusEnum, TaskStatusEnum
from app.schemas.productivity import (
    GoalCreate, GoalUpdate,
    TaskCreate, TaskUpdate,
    PlannerCreate, PlannerUpdate
)

# --- Goals Service ---

def get_goals(db: Session, user_id: uuid.UUID) -> List[Goals]:
    return db.query(Goals).filter(Goals.user_id == user_id).order_by(Goals.created_at.desc()).all()

def create_goal(db: Session, user_id: uuid.UUID, goal_in: GoalCreate) -> Goals:
    db_goal = Goals(
        user_id=user_id,
        **goal_in.model_dump()
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

def update_goal(db: Session, user_id: uuid.UUID, goal_id: uuid.UUID, goal_in: GoalUpdate) -> Goals:
    db_goal = db.query(Goals).filter(Goals.id == goal_id, Goals.user_id == user_id).first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    update_data = goal_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_goal, field, value)
        
    db.commit()
    db.refresh(db_goal)
    return db_goal

def delete_goal(db: Session, user_id: uuid.UUID, goal_id: uuid.UUID):
    db_goal = db.query(Goals).filter(Goals.id == goal_id, Goals.user_id == user_id).first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    db.delete(db_goal)
    db.commit()

# --- Tasks Service ---

def get_tasks(db: Session, user_id: uuid.UUID, goal_id: Optional[uuid.UUID] = None, due_date: Optional[date] = None) -> List[Tasks]:
    query = db.query(Tasks).filter(Tasks.user_id == user_id)
    if goal_id:
        query = query.filter(Tasks.goal_id == goal_id)
    if due_date:
        query = query.filter(Tasks.due_date == due_date)
    return query.order_by(Tasks.created_at.desc()).all()

def create_task(db: Session, user_id: uuid.UUID, task_in: TaskCreate) -> Tasks:
    db_task = Tasks(
        user_id=user_id,
        **task_in.model_dump()
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, user_id: uuid.UUID, task_id: uuid.UUID, task_in: TaskUpdate) -> Tasks:
    db_task = db.query(Tasks).filter(Tasks.id == task_id, Tasks.user_id == user_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
        
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, user_id: uuid.UUID, task_id: uuid.UUID):
    db_task = db.query(Tasks).filter(Tasks.id == task_id, Tasks.user_id == user_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()

# --- Planner Service ---

def get_planner_items(db: Session, user_id: uuid.UUID, plan_date: Optional[date] = None) -> List[Planner]:
    query = db.query(Planner).filter(Planner.user_id == user_id)
    if plan_date:
        query = query.filter(Planner.plan_date == plan_date)
    return query.order_by(Planner.start_time.asc(), Planner.created_at.asc()).all()

def create_planner_item(db: Session, user_id: uuid.UUID, item_in: PlannerCreate) -> Planner:
    db_item = Planner(
        user_id=user_id,
        **item_in.model_dump()
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_planner_item(db: Session, user_id: uuid.UUID, item_id: uuid.UUID, item_in: PlannerUpdate) -> Planner:
    db_item = db.query(Planner).filter(Planner.id == item_id, Planner.user_id == user_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Planner item not found")
    
    update_data = item_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
        
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_planner_item(db: Session, user_id: uuid.UUID, item_id: uuid.UUID):
    db_item = db.query(Planner).filter(Planner.id == item_id, Planner.user_id == user_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Planner item not found")
    
    db.delete(db_item)
    db.commit()
