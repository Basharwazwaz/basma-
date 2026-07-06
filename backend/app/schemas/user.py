from uuid import UUID
from pydantic import BaseModel, EmailStr
from datetime import datetime

class ProfileResponse(BaseModel):
    id: UUID
    first_name: str | None = None
    last_name: str | None = None
    age: int | None = None
    city: str | None = None
    points: int

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    profile: ProfileResponse | None = None

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None
