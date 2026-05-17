from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class EventLogCreate(BaseModel):
    event_type: Optional[str] = None
    description: Optional[str] = None


class EventLogUpdate(BaseModel):
    event_type: Optional[str] = None
    description: Optional[str] = None


class EventLogResponse(BaseModel):
    id: int
    event_type: Optional[str] = None
    description: Optional[str] = None
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True