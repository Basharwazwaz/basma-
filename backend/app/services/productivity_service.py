import uuid
from datetime import date
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.productivity import Goals, Tasks, Planner
from app.schemas.productivity import (
    GoalCreate, GoalUpdate,
    TaskCreate, TaskUpdate,
    PlannerCreate, PlannerUpdate,
)


# ---------------------------------------------------------------------------
# Goals
# ---------------------------------------------------------------------------

async def get_goals(db: AsyncSession, user_id: uuid.UUID) -> List[Goals]:
    result = await db.execute(
        select(Goals).where(Goals.user_id == user_id).order_by(Goals.created_at.desc())
    )
    return result.scalars().all()


async def create_goal(db: AsyncSession, user_id: uuid.UUID, goal_in: GoalCreate) -> Goals:
    db_goal = Goals(user_id=user_id, **goal_in.model_dump())
    db.add(db_goal)
    await db.commit()
    await db.refresh(db_goal)
    return db_goal


async def update_goal(
    db: AsyncSession, user_id: uuid.UUID, goal_id: uuid.UUID, goal_in: GoalUpdate
) -> Goals:
    result = await db.execute(
        select(Goals).where(Goals.id == goal_id, Goals.user_id == user_id)
    )
    db_goal = result.scalars().first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    for field, value in goal_in.model_dump(exclude_unset=True).items():
        setattr(db_goal, field, value)

    await db.commit()
    await db.refresh(db_goal)
    return db_goal


async def delete_goal(db: AsyncSession, user_id: uuid.UUID, goal_id: uuid.UUID) -> None:
    result = await db.execute(
        select(Goals).where(Goals.id == goal_id, Goals.user_id == user_id)
    )
    db_goal = result.scalars().first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    await db.delete(db_goal)
    await db.commit()


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

async def get_tasks(
    db: AsyncSession,
    user_id: uuid.UUID,
    goal_id: Optional[uuid.UUID] = None,
    due_date: Optional[date] = None,
) -> List[Tasks]:
    stmt = select(Tasks).where(Tasks.user_id == user_id)
    if goal_id:
        stmt = stmt.where(Tasks.goal_id == goal_id)
    if due_date:
        stmt = stmt.where(Tasks.due_date == due_date)
    stmt = stmt.order_by(Tasks.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


async def create_task(db: AsyncSession, user_id: uuid.UUID, task_in: TaskCreate) -> Tasks:
    db_task = Tasks(user_id=user_id, **task_in.model_dump())
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def update_task(
    db: AsyncSession, user_id: uuid.UUID, task_id: uuid.UUID, task_in: TaskUpdate
) -> Tasks:
    result = await db.execute(
        select(Tasks).where(Tasks.id == task_id, Tasks.user_id == user_id)
    )
    db_task = result.scalars().first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    for field, value in task_in.model_dump(exclude_unset=True).items():
        setattr(db_task, field, value)

    await db.commit()
    await db.refresh(db_task)
    return db_task


async def delete_task(db: AsyncSession, user_id: uuid.UUID, task_id: uuid.UUID) -> None:
    result = await db.execute(
        select(Tasks).where(Tasks.id == task_id, Tasks.user_id == user_id)
    )
    db_task = result.scalars().first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(db_task)
    await db.commit()


# ---------------------------------------------------------------------------
# Planner
# ---------------------------------------------------------------------------

async def get_planner_items(
    db: AsyncSession, user_id: uuid.UUID, plan_date: Optional[date] = None
) -> List[Planner]:
    stmt = select(Planner).where(Planner.user_id == user_id)
    if plan_date:
        stmt = stmt.where(Planner.plan_date == plan_date)
    stmt = stmt.order_by(Planner.start_time.asc(), Planner.created_at.asc())
    result = await db.execute(stmt)
    return result.scalars().all()


async def create_planner_item(
    db: AsyncSession, user_id: uuid.UUID, item_in: PlannerCreate
) -> Planner:
    db_item = Planner(user_id=user_id, **item_in.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


async def update_planner_item(
    db: AsyncSession, user_id: uuid.UUID, item_id: uuid.UUID, item_in: PlannerUpdate
) -> Planner:
    result = await db.execute(
        select(Planner).where(Planner.id == item_id, Planner.user_id == user_id)
    )
    db_item = result.scalars().first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Planner item not found")

    for field, value in item_in.model_dump(exclude_unset=True).items():
        setattr(db_item, field, value)

    await db.commit()
    await db.refresh(db_item)
    return db_item


async def delete_planner_item(
    db: AsyncSession, user_id: uuid.UUID, item_id: uuid.UUID
) -> None:
    result = await db.execute(
        select(Planner).where(Planner.id == item_id, Planner.user_id == user_id)
    )
    db_item = result.scalars().first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Planner item not found")
    await db.delete(db_item)
    await db.commit()
