from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    profile: "ProfileResponse | None" = None

    class Config:
        from_attributes = True

class ProfileResponse(BaseModel):
    id: str
    first_name: str | None = None
    last_name: str | None = None
    age: int | None = None
    city: str | None = None
    points: int

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None
    gender: str | None = None
    education_level: str | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v
