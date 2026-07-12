"""
Profile service — all business logic for onboarding, profile CRUD, and settings.

All DB-mutating functions operate inside the caller's session; the router is
responsible for committing or rolling back.  The atomic onboarding function
wraps everything in a savepoint so a partial failure reverts cleanly.
"""
from __future__ import annotations

import uuid
from datetime import datetime, date, timezone
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Users, Profiles
from app.models.health import DigitalHabits, Mood
from app.models.productivity import Goals
from app.schemas.profile import (
    OnboardingPayload,
    ProfileUpdate,
    SettingsUpdate,
    MOOD_STATE_MAP,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helper: hours → minutes
# ─────────────────────────────────────────────────────────────────────────────

def _h2m(hours: float) -> int:
    return round(hours * 60)


# ─────────────────────────────────────────────────────────────────────────────
# Onboarding  —  atomic, single-transaction
# ─────────────────────────────────────────────────────────────────────────────

async def onboard_user(
    db: AsyncSession,
    user: Users,
    payload: OnboardingPayload,
) -> Profiles:
    """
    Execute the full onboarding flow atomically:
      1. Update Profile (personal info + interests + targets)
      2. Insert today's DigitalHabits row (screen / social / sleep)
      3. Insert today's Mood row (mood score, stress, state)
      4. Insert one Goal row per goal title selected by the user

    Uses a SAVEPOINT so that if any step fails the entire block rolls back
    and the caller's outer transaction is unaffected.
    """
    today: date = datetime.now(timezone.utc).date()

    async with db.begin_nested():   # SAVEPOINT
        # ── 1. Profile ────────────────────────────────────────────────────
        result = await db.execute(
            select(Profiles).where(Profiles.user_id == user.id)
        )
        profile: Optional[Profiles] = result.scalars().first()

        personal = payload.personal
        digital  = payload.digital
        mental   = payload.mental
        plan     = payload.plan

        if profile is None:
            profile = Profiles(user_id=user.id)
            db.add(profile)

        profile.first_name         = profile.first_name
        profile.last_name          = profile.last_name
        profile.age                = personal.age        if personal.age  is not None else profile.age
        profile.city               = personal.city       or profile.city
        profile.major              = personal.major      or profile.major
        profile.interests          = plan.interests or profile.interests or []
        profile.target_screen_time = _h2m(digital.screen_time_hours)
        profile.target_sleep_time  = _h2m(digital.sleep_hours)

        await db.flush()

        # ── 2. DigitalHabits (upsert by user_id + today) ──────────────────
        habits_result = await db.execute(
            select(DigitalHabits).where(
                DigitalHabits.user_id == user.id,
                DigitalHabits.record_date == today,
            )
        )
        habits: Optional[DigitalHabits] = habits_result.scalars().first()

        if habits is None:
            habits = DigitalHabits(user_id=user.id, record_date=today)
            db.add(habits)

        habits.screen_time_minutes   = _h2m(digital.screen_time_hours)
        habits.social_media_minutes  = _h2m(digital.social_media_hours)
        habits.sleep_minutes         = _h2m(digital.sleep_hours)

        await db.flush()

        # ── 3. Mood (upsert by user_id + today) ───────────────────────────
        mood_result = await db.execute(
            select(Mood).where(
                Mood.user_id == user.id,
                Mood.record_date == today,
            )
        )
        mood_row: Optional[Mood] = mood_result.scalars().first()

        # Map Arabic mood label → DB enum value
        raw_state    = mental.mood_state or ""
        db_mood_state = MOOD_STATE_MAP.get(raw_state, "NEUTRAL")

        if mood_row is None:
            mood_row = Mood(user_id=user.id, record_date=today)
            db.add(mood_row)

        mood_row.mood_score  = mental.mood_score
        mood_row.stress_score = mental.stress_score
        mood_row.mood_state  = db_mood_state

        await db.flush()

        # ── 4. Goals ──────────────────────────────────────────────────────
        # Insert only new goals (avoid duplicating if onboarding is re-run)
        existing_goals_result = await db.execute(
            select(Goals.title).where(Goals.user_id == user.id)
        )
        existing_titles = {row for row in existing_goals_result.scalars().all()}

        for goal_title in plan.goals:
            if goal_title not in existing_titles:
                goal = Goals(
                    user_id=user.id,
                    title=goal_title,
                    category="عام",
                    status="NOT_STARTED",
                    progress_percent=0,
                )
                db.add(goal)

        await db.flush()

    # Caller commits
    await db.refresh(profile)
    return profile


# ─────────────────────────────────────────────────────────────────────────────
# GET /profile — full join
# ─────────────────────────────────────────────────────────────────────────────

async def get_full_profile(db: AsyncSession, user_id: uuid.UUID) -> Optional[Users]:
    result = await db.execute(
        select(Users)
        .options(selectinload(Users.profile))
        .where(Users.id == user_id)
    )
    return result.scalars().first()


# ─────────────────────────────────────────────────────────────────────────────
# PUT /profile — partial update (personal info + interests + targets)
# ─────────────────────────────────────────────────────────────────────────────

async def update_profile(
    db: AsyncSession,
    user: Users,
    data: ProfileUpdate,
) -> Profiles:
    result = await db.execute(
        select(Profiles).where(Profiles.user_id == user.id)
    )
    profile = result.scalars().first()

    if profile is None:
        profile = Profiles(user_id=user.id)
        db.add(profile)
        await db.flush()

    # Only update fields that were explicitly sent (exclude_unset semantics)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    profile.updated_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(profile)
    return profile


# ─────────────────────────────────────────────────────────────────────────────
# PUT /settings — language / theme / notifications_enabled only
# ─────────────────────────────────────────────────────────────────────────────

async def update_settings(
    db: AsyncSession,
    user: Users,
    data: SettingsUpdate,
) -> Profiles:
    result = await db.execute(
        select(Profiles).where(Profiles.user_id == user.id)
    )
    profile = result.scalars().first()

    if profile is None:
        profile = Profiles(user_id=user.id)
        db.add(profile)
        await db.flush()

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    profile.updated_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(profile)
    return profile
