from pydantic import BaseModel
from datetime import datetime


class ConversationBase(BaseModel):
    user_id: int
    personality_id: int


class ConversationCreate(ConversationBase):
    title: str | None = None


class ConversationUpdate(BaseModel):
    user_id: int | None = None
    personality_id: int | None = None
    title: str | None = None


class ConversationOut(ConversationBase):
    id: int
    title: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True