from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class NotificationBase(BaseModel):
    user_id: int
    title: str
    content: str
    is_read: bool = False


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    user_id: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None
    is_read: Optional[bool] = None


class NotificationResponse(NotificationBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
