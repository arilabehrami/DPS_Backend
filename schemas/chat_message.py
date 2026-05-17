from pydantic import BaseModel
from datetime import datetime


class ChatMessageCreate(BaseModel):
    conversation_id: int
    sender: str
    content: str


class ChatMessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True