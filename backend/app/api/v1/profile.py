"""
Profile & Settings routes — all protected by get_current_user.

Endpoints:
  POST /profile/onboarding          — atomic multi-domain wizard submission
  GET  /profile                     — full profile with user join
  GET  /profile/export              — full user data export (GDPR)
  PUT  /profile                     — partial personal-info update
  PUT  /profile/settings            — language / theme / notifications
  PUT  /user/me                     — email + display name (user-level)
"""
from __future__ import annotations

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import Users
from app.models.auth import RefreshTokens
from app.models.health import Mood, DigitalHabits
from app.models.productivity import Goals, Tasks, Planner
from app.models.gamification import UserChallenges, Achievements
from app.models.analytics import WeeklyReports, AIInsights
from app.models.notifications import Notifications
from app.models.coach import CoachMessages
from app.schemas.profile import (
    DataExportResponse,
    FullUserResponse,
    OnboardingPayload,
    ProfileResponse,
    ProfileUpdate,
    SettingsUpdate,
    UserMeUpdate,
)
from app.services import profile_service

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# POST /profile/onboarding
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/onboarding",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit completed onboarding wizard",
    description=(
        "Accepts all 5 wizard steps in one payload and atomically creates / "
        "updates Profile, DigitalHabits, Mood, and Goals inside a single "
        "database savepoint. Safe to re-call (idempotent for habits & mood, "
        "deduplicates goals by title)."
    ),
)
async def submit_onboarding(
    payload: OnboardingPayload,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    profile = await profile_service.onboard_user(db, current_user, payload)
    await db.commit()
    return profile


# ─────────────────────────────────────────────────────────────────────────────
# GET /profile
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=FullUserResponse,
    summary="Get full profile",
    description="Returns the authenticated user with their nested profile data.",
)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    user = await profile_service.get_full_profile(db, current_user.id)
    if user is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return user


# ─────────────────────────────────────────────────────────────────────────────
# GET /profile/export
# ─────────────────────────────────────────────────────────────────────────────

def _rows_to_dicts(rows) -> list[dict]:
    return [
        {k: str(v) if hasattr(v, "hex") else v.isoformat() if hasattr(v, "isoformat") else v
         for k, v in row.__dict__.items() if not k.startswith("_")}
        for row in rows
    ]


@router.get(
    "/export",
    response_model=DataExportResponse,
    summary="Export all user data",
    description="Returns all user data for GDPR compliance (profile, moods, tasks, etc.).",
)
async def export_data(
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    uid = current_user.id
    user = await profile_service.get_full_profile(db, uid)
    if user is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    goals_r = await db.execute(select(Goals).where(Goals.user_id == uid))
    tasks_r = await db.execute(select(Tasks).where(Tasks.user_id == uid))
    planner_r = await db.execute(select(Planner).where(Planner.user_id == uid))
    moods_r = await db.execute(select(Mood).where(Mood.user_id == uid))
    habits_r = await db.execute(select(DigitalHabits).where(DigitalHabits.user_id == uid))
    ach_r = await db.execute(select(Achievements).where(Achievements.user_id == uid))
    uc_r = await db.execute(select(UserChallenges).where(UserChallenges.user_id == uid))
    wr_r = await db.execute(select(WeeklyReports).where(WeeklyReports.user_id == uid))
    ai_r = await db.execute(select(AIInsights).where(AIInsights.user_id == uid))
    notif_r = await db.execute(select(Notifications).where(Notifications.user_id == uid))
    coach_r = await db.execute(select(CoachMessages).where(CoachMessages.user_id == uid))

    return DataExportResponse(
        user=user,
        goals=_rows_to_dicts(goals_r.scalars().all()),
        tasks=_rows_to_dicts(tasks_r.scalars().all()),
        planner=_rows_to_dicts(planner_r.scalars().all()),
        moods=_rows_to_dicts(moods_r.scalars().all()),
        digital_habits=_rows_to_dicts(habits_r.scalars().all()),
        achievements=_rows_to_dicts(ach_r.scalars().all()),
        user_challenges=_rows_to_dicts(uc_r.scalars().all()),
        weekly_reports=_rows_to_dicts(wr_r.scalars().all()),
        ai_insights=_rows_to_dicts(ai_r.scalars().all()),
        notifications=_rows_to_dicts(notif_r.scalars().all()),
        coach_messages=_rows_to_dicts(coach_r.scalars().all()),
        exported_at=datetime.now(timezone.utc),
    )


# ─────────────────────────────────────────────────────────────────────────────
# PUT /profile
# ─────────────────────────────────────────────────────────────────────────────

@router.put(
    "/",
    response_model=ProfileResponse,
    summary="Update personal profile info",
    description=(
        "Partial update — only fields included in the request body are changed. "
        "Fields omitted from the payload are left untouched (exclude_unset semantics)."
    ),
)
async def update_profile(
    data: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    profile = await profile_service.update_profile(db, current_user, data)
    await db.commit()
    return profile


# ─────────────────────────────────────────────────────────────────────────────
# PUT /profile/settings
# ─────────────────────────────────────────────────────────────────────────────

@router.put(
    "/settings",
    response_model=ProfileResponse,
    summary="Update app settings",
    description=(
        "Update language ('ar'|'en'), theme ('light'|'dark'), and "
        "notifications_enabled. Only the provided fields are written."
    ),
)
async def update_settings(
    data: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    profile = await profile_service.update_settings(db, current_user, data)
    await db.commit()
    return profile


# ─────────────────────────────────────────────────────────────────────────────
# PUT /user/me  (user-level data: email + display name)
# ─────────────────────────────────────────────────────────────────────────────

@router.put(
    "/me",
    response_model=FullUserResponse,
    summary="Update user account data",
    description=(
        "Update email and/or display name on the user and profile rows. "
        "Returns 409 if the requested email is already taken by another account."
    ),
)
async def update_user_me(
    data: UserMeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    # ── Email uniqueness check ────────────────────────────────────────────
    if data.email and data.email != current_user.email:
        conflict = await db.execute(
            select(Users).where(Users.email == data.email)
        )
        if conflict.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with that email address already exists.",
            )
        current_user.email = data.email

    # ── Profile name fields (if provided) ────────────────────────────────
    if data.first_name is not None or data.last_name is not None:
        profile_update = ProfileUpdate(
            first_name=data.first_name,
            last_name=data.last_name,
        )
        await profile_service.update_profile(db, current_user, profile_update)

    await db.commit()

    # Return refreshed user + profile
    user = await profile_service.get_full_profile(db, current_user.id)
    return user


# ─────────────────────────────────────────────────────────────────────────────
# DELETE /profile  (account deletion)
# ─────────────────────────────────────────────────────────────────────────────

@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete current user account",
    description=(
        "Soft-deactivates the user account (sets is_active=False). "
        "User data is retained for audit purposes. This action is irreversible."
    ),
)
async def delete_account(
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    current_user.is_active = False
    # Revoke all refresh tokens to prevent further use
    tokens_result = await db.execute(
        select(RefreshTokens).where(RefreshTokens.user_id == current_user.id)
    )
    for token in tokens_result.scalars().all():
        token.is_revoked = True
    await db.commit()
