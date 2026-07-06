"""
Profile & Settings routes — all protected by get_current_user.

Endpoints:
  POST /profile/onboarding          — atomic multi-domain wizard submission
  GET  /profile                     — full profile with user join
  PUT  /profile                     — partial personal-info update
  PUT  /profile/settings            — language / theme / notifications
  PUT  /user/me                     — email + display name (user-level)
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import Users
from app.schemas.profile import (
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
