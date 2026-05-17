from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ChatMessageCreate(BaseModel):
    content: Optional[str] = None
    sender: Optional[str] = None
    conversation_id: Optional[int] = None


class ChatMessageUpdate(BaseModel):
    content: Optional[str] = None
    sender: Optional[str] = None


class ChatMessageResponse(BaseModel):
    id: int
    content: Optional[str] = None
    sender: Optional[str] = None
    conversation_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True