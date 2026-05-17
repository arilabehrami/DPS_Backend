from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class SessionCreate(BaseModel):
    user_id: Optional[int] = None
    token: Optional[str] = None


class SessionUpdate(BaseModel):
    token: Optional[str] = None


class SessionResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    token: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True