from __future__ import annotations

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


# ─────────────────────────────────────────────────────────────────────────────
# Onboarding sub-schemas (one per wizard step)
# ─────────────────────────────────────────────────────────────────────────────

class PersonalInfo(BaseModel):
    """Step 0 — age, city, major. All optional so partial saves work."""
    age: Optional[int] = None
    city: Optional[str] = None
    major: Optional[str] = None

    @field_validator("age")
    @classmethod
    def age_must_be_positive(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("Age must be a positive integer")
        return v


class DigitalBehavior(BaseModel):
    """Step 1 — current screen / social-media / sleep usage (hours from slider)."""
    # current daily usage submitted by the user (stored in DigitalHabits table)
    screen_time_hours: float           # 1–16 h/day
    social_media_hours: float          # 0–10 h/day
    sleep_hours: float                 # 3–12 h/night

    @field_validator("screen_time_hours", "social_media_hours", "sleep_hours")
    @classmethod
    def must_be_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Value must not be negative")
        return v


class MentalState(BaseModel):
    """Step 2 — mood score, stress score, mood label."""
    mood_score: int        # 1–10
    stress_score: int      # 1–10
    mood_state: Optional[str] = None   # e.g. "متوتر", "هادئ", ...

    @field_validator("mood_score", "stress_score")
    @classmethod
    def score_range(cls, v: int) -> int:
        if not (1 <= v <= 10):
            raise ValueError("Score must be between 1 and 10")
        return v


MOOD_STATE_MAP: dict[str, str] = {
    "متوتر":    "BAD",
    "هادئ":     "GOOD",
    "متحمّس":   "EXCELLENT",
    "متعب":     "NEUTRAL",
}


class GoalsAndInterests(BaseModel):
    """Steps 3 + 4 — goal titles from predefined list + interests array."""
    goals: List[str] = []
    interests: List[str] = []

    @field_validator("goals")
    @classmethod
    def at_least_one_goal(cls, v: List[str]) -> List[str]:
        if len(v) == 0:
            raise ValueError("At least one goal must be selected")
        return v


class OnboardingPayload(BaseModel):
    """
    Single atomic payload for POST /profile/onboarding.
    The frontend wizard collects all 5 steps before submitting.
    """
    personal: PersonalInfo
    digital: DigitalBehavior
    mental: MentalState
    plan: GoalsAndInterests


# ─────────────────────────────────────────────────────────────────────────────
# Profile response schemas
# ─────────────────────────────────────────────────────────────────────────────

class ProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    major: Optional[str] = None
    target_screen_time: Optional[int] = None    # minutes/day
    target_sleep_time: Optional[int] = None     # minutes/night
    points: int
    interests: Optional[List[str]] = []
    language: str
    theme: str
    notifications_enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FullUserResponse(BaseModel):
    """Returned by GET /profile — user + nested profile."""
    id: UUID
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    profile: Optional[ProfileResponse] = None

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────────────────────
# Update schemas  (all fields Optional for PATCH semantics via exclude_unset)
# ─────────────────────────────────────────────────────────────────────────────

class ProfileUpdate(BaseModel):
    """PUT /profile — personal info only."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    major: Optional[str] = None
    interests: Optional[List[str]] = None
    target_screen_time: Optional[int] = None
    target_sleep_time: Optional[int] = None

    @field_validator("age")
    @classmethod
    def age_positive(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("Age must be a positive integer")
        return v


class SettingsUpdate(BaseModel):
    """PUT /settings — language / theme / notifications only."""
    language: Optional[str] = None
    theme: Optional[str] = None
    notifications_enabled: Optional[bool] = None

    @field_validator("language")
    @classmethod
    def valid_language(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("ar", "en"):
            raise ValueError("Language must be 'ar' or 'en'")
        return v

    @field_validator("theme")
    @classmethod
    def valid_theme(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("light", "dark"):
            raise ValueError("Theme must be 'light' or 'dark'")
        return v


class UserMeUpdate(BaseModel):
    """PUT /user/me — user-level fields (email, display name)."""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
