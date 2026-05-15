from pydantic import BaseModel
from datetime import datetime


class MessageBase(BaseModel):
    conversation_id: int
    sender: str
    content: str


class MessageCreate(MessageBase):
    pass


class MessageUpdate(BaseModel):
    sender: str | None = None
    content: str | None = None
    conversation_id: int | None = None


class MessageOut(MessageBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True