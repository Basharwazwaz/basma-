"""
Smart Study Plan Generator
Generates an optimized weekly study plan based on user goals, tasks, and habits.
"""

import uuid
from dataclasses import dataclass
from datetime import date, timedelta, time
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.productivity import Goals, Tasks, Planner
from app.models.health import DigitalHabits


@dataclass
class PlanEvent:
    title: str
    plan_date: date
    start_time: time
    end_time: time
    event_type: str  # study, break, review, health


async def generate_study_plan(
    db: AsyncSession,
    user_id: uuid.UUID,
    target_week_start: Optional[date] = None,
) -> List[PlanEvent]:
    """
    Generate a smart weekly study plan based on:
    - User's active goals
    - Pending tasks and their due dates
    - Historical study patterns (from habits data)
    """

    today = date.today()
    if target_week_start is None:
        # Start from next Monday
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        target_week_start = today + timedelta(days=days_until_monday)

    # ── Fetch user data ────────────────────────────────────────────────────
    goals_result = await db.execute(
        select(Goals).where(
            Goals.user_id == user_id,
            Goals.status.in_(["NOT_STARTED", "IN_PROGRESS"]),
        )
    )
    active_goals = goals_result.scalars().all()

    tasks_result = await db.execute(
        select(Tasks).where(
            Tasks.user_id == user_id,
            Tasks.is_completed == False,
        ).order_by(Tasks.due_date.asc().nullslast())
    )
    pending_tasks = tasks_result.scalars().all()

    # Fetch habits to understand available study time
    habits_result = await db.execute(
        select(DigitalHabits).where(
            DigitalHabits.user_id == user_id,
            DigitalHabits.record_date >= today - timedelta(days=14),
        )
    )
    habits = habits_result.scalars().all()

    # ── Determine study capacity ───────────────────────────────────────────
    # Average free time = 16h awake - screen time - sleep
    if habits:
        avg_screen = sum(h.screen_time_minutes for h in habits) / len(habits)
        avg_sleep = sum(h.sleep_minutes for h in habits) / len(habits)
    else:
        avg_screen = 240  # 4 hours default
        avg_sleep = 420  # 7 hours default

    awake_minutes = 16 * 60  # 16 hours
    free_minutes = max(120, awake_minutes - avg_screen - avg_sleep)  # at least 2h free
    study_minutes_per_day = min(240, int(free_minutes * 0.4))  # max 4h study, 40% of free time

    # ── Generate plan ──────────────────────────────────────────────────────
    events: List[PlanEvent] = []

    # Assign tasks to days based on priority (due date first, then by goal importance)
    tasks_by_day = _distribute_tasks(pending_tasks, target_week_start, study_minutes_per_day)

    for day_offset in range(7):
        current_date = target_week_start + timedelta(days=day_offset)
        day_tasks = tasks_by_day.get(day_offset, [])

        if not day_tasks:
            # Rest day — add a light review session
            events.append(PlanEvent(
                title="مراجعة خفيفة",
                plan_date=current_date,
                start_time=time(18, 0),
                end_time=time(18, 30),
                event_type="review",
            ))
            continue

        # Schedule study blocks
        current_time = time(9, 0)  # Start at 9 AM
        minutes_used = 0

        for task in day_tasks:
            # Calculate block duration (split long tasks into 45-min blocks)
            task_minutes = min(45, study_minutes_per_day - minutes_used)
            if task_minutes <= 0:
                break

            end_hour = current_time.hour + (current_time.minute + task_minutes) // 60
            end_min = (current_time.minute + task_minutes) % 60

            events.append(PlanEvent(
                title=task.title,
                plan_date=current_date,
                start_time=current_time,
                end_time=time(min(end_hour, 23), end_min),
                event_type="study",
            ))

            minutes_used += task_minutes

            # Add 10-minute break after each study block
            break_start_min = current_time.minute + task_minutes + 10
            break_start_hour = current_time.hour + break_start_min // 60
            break_start_min = break_start_min % 60

            if minutes_used < study_minutes_per_day:
                events.append(PlanEvent(
                    title="استراحة",
                    plan_date=current_date,
                    start_time=time(min(break_start_hour, 23), break_start_min),
                    end_time=time(min(break_start_hour, 23), break_start_min + 10),
                    event_type="break",
                ))

            current_time = time(min(break_start_hour, 23), (break_start_min + 10) % 60)

    return events


def _distribute_tasks(
    tasks: List,
    week_start: date,
    minutes_per_day: int,
) -> dict:
    """Distribute pending tasks across the week intelligently."""
    distribution = {}

    # Priority sort: tasks with due dates first, then by creation order
    sorted_tasks = sorted(tasks, key=lambda t: (t.due_date is None, t.due_date or date.max))

    task_idx = 0
    for day in range(7):
        if task_idx >= len(sorted_tasks):
            break

        day_minutes = 0
        day_tasks = []

        while task_idx < len(sorted_tasks) and day_minutes < minutes_per_day:
            task = sorted_tasks[task_idx]

            # If task is due before this day, prioritize it
            if task.due_date and task.due_date < week_start + timedelta(days=day):
                day_tasks.append(task)
                day_minutes += 45
                task_idx += 1
                continue

            # If task is due on this day or this week, schedule it
            if task.due_date is None or task.due_date <= week_start + timedelta(days=day + 2):
                day_tasks.append(task)
                day_minutes += 45
                task_idx += 1
                continue

            break

        if day_tasks:
            distribution[day] = day_tasks

    # Fill remaining days with leftover tasks
    remaining = sorted_tasks[task_idx:]
    for day in range(7):
        if not remaining:
            break
        if day not in distribution:
            distribution[day] = [remaining.pop(0)]

    return distribution


async def save_plan_to_planner(
    db: AsyncSession,
    user_id: uuid.UUID,
    events: List[PlanEvent],
) -> List[Planner]:
    """Save generated plan events to the planner table."""
    saved = []
    for event in events:
        db_event = Planner(
            user_id=user_id,
            title=event.title,
            plan_date=event.plan_date,
            start_time=event.start_time,
            end_time=event.end_time,
        )
        db.add(db_event)
        saved.append(db_event)

    await db.commit()
    for ev in saved:
        await db.refresh(ev)
    return saved
