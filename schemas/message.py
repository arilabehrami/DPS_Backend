from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class MessageBase(BaseModel):
    conversation_id: int
    workspace_id: int
    sender_type: str
    sender_user_id: Optional[int] = None
    sender_personality_id: Optional[int] = None
    content: str


class MessageCreate(MessageBase):
    pass


class MessageUpdate(BaseModel):
    conversation_id: Optional[int] = None
    workspace_id: Optional[int] = None
    sender_type: Optional[str] = None
    sender_user_id: Optional[int] = None
    sender_personality_id: Optional[int] = None
    content: Optional[str] = None


class MessageResponse(MessageBase):
    id: int
    timestamp: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
