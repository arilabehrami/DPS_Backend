from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class EventLogBase(BaseModel):
    user_id: int
    workspace_id: Optional[int] = None
    event_type: str
    description: Optional[str] = None


class EventLogCreate(EventLogBase):
    pass


class EventLogUpdate(BaseModel):
    user_id: Optional[int] = None
    workspace_id: Optional[int] = None
    event_type: Optional[str] = None
    description: Optional[str] = None


class EventLogResponse(EventLogBase):
    id: int
    timestamp: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
