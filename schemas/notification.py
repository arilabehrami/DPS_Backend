from typing import Optional
from pydantic import BaseModel


class NotificationCreate(BaseModel):
    user_id: Optional[int] = None
    title: Optional[str] = None
    is_read: Optional[bool] = None


class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    is_read: Optional[bool] = None


class NotificationResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    title: Optional[str] = None
    is_read: Optional[bool] = None

    class Config:
        from_attributes = True