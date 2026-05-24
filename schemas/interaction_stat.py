from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class InteractionStatBase(BaseModel):
    user_id: int
    personality_id: int
    workspace_id: int
    conversation_id: Optional[int] = None
    total_messages: int = 0
    last_interaction: Optional[datetime] = None


class InteractionStatCreate(InteractionStatBase):
    pass


class InteractionStatUpdate(BaseModel):
    user_id: Optional[int] = None
    personality_id: Optional[int] = None
    workspace_id: Optional[int] = None
    conversation_id: Optional[int] = None
    total_messages: Optional[int] = None
    last_interaction: Optional[datetime] = None


class InteractionStatResponse(InteractionStatBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
