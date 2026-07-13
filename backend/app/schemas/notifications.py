from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
class NotificationBase(BaseModel):
    title: str = Field(..., max_length=200)
    message: Optional[str] = Field(None, max_length=1000)
    is_read: bool = False
    action_url: Optional[str] = Field(None, max_length=500)

class NotificationCreate(NotificationBase):
    user_id: str

class NotificationUpdate(BaseModel):
    is_read: bool

class NotificationResponse(NotificationBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True
