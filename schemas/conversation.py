from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ConversationBase(BaseModel):
    user_id: int
    personality_id: int
    workspace_id: int
    title: Optional[str] = None


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(BaseModel):
    user_id: Optional[int] = None
    personality_id: Optional[int] = None
    workspace_id: Optional[int] = None
    title: Optional[str] = None


class ConversationResponse(ConversationBase):
    id: int
    started_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
