from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import date

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import Users
from app.schemas.productivity import (
    GoalCreate, GoalUpdate, GoalResponse,
    TaskCreate, TaskUpdate, TaskResponse,
    PlannerCreate, PlannerUpdate, PlannerResponse
)
from app.services import productivity_service

router = APIRouter()

# --- Goals ---

@router.get("/goals", response_model=List[GoalResponse])
def get_goals(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Retrieve all goals for the current user."""
    return productivity_service.get_goals(db, current_user.id)

@router.post("/goals", response_model=GoalResponse)
def create_goal(
    goal_in: GoalCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Create a new goal."""
    return productivity_service.create_goal(db, current_user.id, goal_in)

@router.put("/goals/{goal_id}", response_model=GoalResponse)
def update_goal(
    goal_id: uuid.UUID,
    goal_in: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Update a goal."""
    return productivity_service.update_goal(db, current_user.id, goal_id, goal_in)

@router.delete("/goals/{goal_id}")
def delete_goal(
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Delete a goal."""
    productivity_service.delete_goal(db, current_user.id, goal_id)
    return {"status": "success"}

# --- Tasks ---

@router.get("/tasks", response_model=List[TaskResponse])
def get_tasks(
    goal_id: Optional[uuid.UUID] = None,
    due_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Retrieve tasks. Can be filtered by goal_id or due_date."""
    return productivity_service.get_tasks(db, current_user.id, goal_id, due_date)

@router.post("/tasks", response_model=TaskResponse)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Create a new task."""
    return productivity_service.create_task(db, current_user.id, task_in)

@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: uuid.UUID,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Update a task."""
    return productivity_service.update_task(db, current_user.id, task_id, task_in)

@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Delete a task."""
    productivity_service.delete_task(db, current_user.id, task_id)
    return {"status": "success"}

# --- Planner ---

@router.get("/planner", response_model=List[PlannerResponse])
def get_planner_items(
    plan_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Retrieve planner schedule items. Can be filtered by date."""
    return productivity_service.get_planner_items(db, current_user.id, plan_date)

@router.post("/planner", response_model=PlannerResponse)
def create_planner_item(
    item_in: PlannerCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Schedule a new item in the planner."""
    return productivity_service.create_planner_item(db, current_user.id, item_in)

@router.put("/planner/{item_id}", response_model=PlannerResponse)
def update_planner_item(
    item_id: uuid.UUID,
    item_in: PlannerUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Update a scheduled item."""
    return productivity_service.update_planner_item(db, current_user.id, item_id, item_in)

@router.delete("/planner/{item_id}")
def delete_planner_item(
    item_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Remove a scheduled item."""
    productivity_service.delete_planner_item(db, current_user.id, item_id)
    return {"status": "success"}
