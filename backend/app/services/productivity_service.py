import uuid
from datetime import date
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import func
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

async def get_goals(db: AsyncSession, user_id: uuid.UUID, skip: int = 0, limit: int = 50) -> List[Goals]:
    result = await db.execute(
        select(Goals)
        .where(Goals.user_id == user_id)
        .order_by(Goals.created_at.desc())
        .offset(skip)
        .limit(limit)
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

    if db_goal.status == "COMPLETED":
        from app.services.points_service import add_points
        await add_points(db, user_id, 25, f"إنجاز الهدف: {db_goal.title}")

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
    skip: int = 0,
    limit: int = 50,
) -> List[Tasks]:
    stmt = select(Tasks).where(Tasks.user_id == user_id)
    if goal_id:
        stmt = stmt.where(Tasks.goal_id == goal_id)
    if due_date:
        stmt = stmt.where(Tasks.due_date == due_date)
    stmt = stmt.order_by(Tasks.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def create_task(db: AsyncSession, user_id: uuid.UUID, task_in: TaskCreate) -> Tasks:
    db_task = Tasks(user_id=user_id, **task_in.model_dump())
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)

    # ── Achievement: first task created ────────────────────────────────────
    from app.services.gamification_service import award_achievement
    from sqlalchemy import func
    count_result = await db.execute(
        select(func.count()).select_from(Tasks).where(Tasks.user_id == user_id)
    )
    task_count = count_result.scalar()
    if task_count == 1:
        await award_achievement(
            db, user_id,
            title="أول خطوة",
            description="أنشأت أول مهمة لك. استمر في التخطيط!",
            icon="🎯",
        )

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

    was_not_completed = not db_task.is_completed

    for field, value in task_in.model_dump(exclude_unset=True).items():
        setattr(db_task, field, value)

    # ── Achievement: first task completed ──────────────────────────────────
    if was_not_completed and db_task.is_completed:
        from app.services.gamification_service import award_achievement
        from app.services.points_service import add_points
        completed_count = await db.scalar(
            select(func.count(Tasks.id)).where(
                Tasks.user_id == user_id,
                Tasks.is_completed == True,
            )
        )
        if completed_count == 1:
            await award_achievement(
                db, user_id,
                title="إنجاز مهم",
                description="أكملت أول مهمة! استمر في الحفاظ على الإنتاجية.",
                icon="✅",
            )
        await add_points(db, user_id, 10, "إكمال مهمة")

    # ── Auto-update goal progress based on completed tasks ─────────────────
    if db_task.goal_id:
        total_tasks = await db.scalar(
            select(func.count(Tasks.id)).where(
                Tasks.goal_id == db_task.goal_id, Tasks.user_id == user_id
            )
        )
        completed_tasks = await db.scalar(
            select(func.count(Tasks.id)).where(
                Tasks.goal_id == db_task.goal_id,
                Tasks.user_id == user_id,
                Tasks.is_completed == True,
            )
        )
        if total_tasks and total_tasks > 0:
            new_progress = int((completed_tasks / total_tasks) * 100)
            result = await db.execute(
                select(Goals).where(Goals.id == db_task.goal_id, Goals.user_id == user_id)
            )
            db_goal = result.scalars().first()
            if db_goal:
                db_goal.progress_percent = new_progress
                if new_progress == 100:
                    db_goal.status = "COMPLETED"

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
    db: AsyncSession, user_id: uuid.UUID, plan_date: Optional[date] = None,
    skip: int = 0, limit: int = 50,
) -> List[Planner]:
    stmt = select(Planner).where(Planner.user_id == user_id)
    if plan_date:
        stmt = stmt.where(Planner.plan_date == plan_date)
    stmt = stmt.order_by(Planner.start_time.asc(), Planner.created_at.asc()).offset(skip).limit(limit)
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

    # ── When a planner session is completed, also mark the linked task done ──
    if db_item.is_completed and db_item.goal_id:
        # Find a matching pending task with same title and goal_id
        task_result = await db.execute(
            select(Tasks).where(
                Tasks.user_id == user_id,
                Tasks.goal_id == db_item.goal_id,
                Tasks.title == db_item.title,
                Tasks.is_completed == False,
            ).limit(1)
        )
        matching_task = task_result.scalars().first()
        if matching_task:
            matching_task.is_completed = True
            matching_task.status = "DONE"
            from app.services.points_service import add_points
            await add_points(db, user_id, 10, f"إكمال جلسة: {db_item.title}")
            # Goal progress update is handled by update_task, but here we do it directly
            # since we only set the task flag without calling update_task
            total_tasks = await db.scalar(
                select(func.count(Tasks.id)).where(
                    Tasks.goal_id == db_item.goal_id, Tasks.user_id == user_id
                )
            )
            completed_tasks = await db.scalar(
                select(func.count(Tasks.id)).where(
                    Tasks.goal_id == db_item.goal_id,
                    Tasks.user_id == user_id,
                    Tasks.is_completed == True,
                )
            )
            if total_tasks and total_tasks > 0:
                new_progress = int((completed_tasks / total_tasks) * 100)
                goal_result = await db.execute(
                    select(Goals).where(Goals.id == db_item.goal_id, Goals.user_id == user_id)
                )
                db_goal = goal_result.scalars().first()
                if db_goal:
                    db_goal.progress_percent = new_progress
                    if new_progress >= 100:
                        db_goal.status = "COMPLETED"

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
