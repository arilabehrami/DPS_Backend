from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SessionBase(BaseModel):
    user_id: int
    token: str
    started_at: datetime
    expires_at: datetime


class SessionCreate(SessionBase):
    pass


class SessionUpdate(BaseModel):
    user_id: Optional[int] = None
    token: Optional[str] = None
    started_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class SessionResponse(SessionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
