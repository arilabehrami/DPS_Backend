from pydantic import BaseModel
from datetime import datetime


class EventLogCreate(BaseModel):
    event: str


class EventLogResponse(BaseModel):
    id: int
    event: str
    created_at: datetime

    class Config:
        from_attributes = True