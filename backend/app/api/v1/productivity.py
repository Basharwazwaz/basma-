import uuid
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import Users
from app.schemas.productivity import (
    GoalCreate, GoalUpdate, GoalResponse,
    TaskCreate, TaskUpdate, TaskResponse,
    PlannerCreate, PlannerUpdate, PlannerResponse,
)
from app.services import productivity_service

router = APIRouter()


# ---------------------------------------------------------------------------
# Goals
# ---------------------------------------------------------------------------

@router.get("/goals", response_model=List[GoalResponse])
async def get_goals(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Retrieve all goals for the current user."""
    return await productivity_service.get_goals(db, current_user.id, skip=skip, limit=limit)


@router.post("/goals", response_model=GoalResponse)
async def create_goal(
    goal_in: GoalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Create a new goal."""
    return await productivity_service.create_goal(db, current_user.id, goal_in)


@router.put("/goals/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str,
    goal_in: GoalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Update a goal."""
    return await productivity_service.update_goal(db, current_user.id, goal_id, goal_in)


@router.delete("/goals/{goal_id}")
async def delete_goal(
    goal_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Delete a goal."""
    await productivity_service.delete_goal(db, current_user.id, goal_id)
    return {"status": "success"}


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(
    goal_id: Optional[str] = None,
    due_date: Optional[date] = None,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Retrieve tasks. Can be filtered by goal_id or due_date."""
    return await productivity_service.get_tasks(db, current_user.id, goal_id, due_date, skip=skip, limit=limit)


@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Create a new task."""
    return await productivity_service.create_task(db, current_user.id, task_in)


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_in: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Update a task."""
    return await productivity_service.update_task(db, current_user.id, task_id, task_in)


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Delete a task."""
    await productivity_service.delete_task(db, current_user.id, task_id)
    return {"status": "success"}


# ---------------------------------------------------------------------------
# Planner
# ---------------------------------------------------------------------------

@router.get("/planner", response_model=List[PlannerResponse])
async def get_planner_items(
    plan_date: Optional[date] = None,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Retrieve planner schedule items. Can be filtered by date."""
    return await productivity_service.get_planner_items(db, current_user.id, plan_date, skip=skip, limit=limit)


@router.post("/planner", response_model=PlannerResponse)
async def create_planner_item(
    item_in: PlannerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Schedule a new item in the planner."""
    return await productivity_service.create_planner_item(db, current_user.id, item_in)


@router.put("/planner/{item_id}", response_model=PlannerResponse)
async def update_planner_item(
    item_id: str,
    item_in: PlannerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Update a scheduled item."""
    return await productivity_service.update_planner_item(
        db, current_user.id, item_id, item_in
    )


@router.delete("/planner/{item_id}")
async def delete_planner_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Remove a scheduled item."""
    await productivity_service.delete_planner_item(db, current_user.id, item_id)
    return {"status": "success"}
