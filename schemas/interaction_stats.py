from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class InteractionStatsCreate(BaseModel):
    user_id: int
    persona_id: Optional[int] = None
    total_messages: Optional[int] = None
    total_sessions: Optional[int] = None


class InteractionStatsUpdate(BaseModel):
    total_messages: Optional[int] = None
    total_sessions: Optional[int] = None
    last_interaction: Optional[datetime] = None


class InteractionStatsResponse(BaseModel):
    id: int
    user_id: int
    persona_id: Optional[int] = None
    total_messages: Optional[int] = None
    total_sessions: Optional[int] = None
    last_interaction: Optional[datetime] = None

    class Config:
        from_attributes = True