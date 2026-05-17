from typing import Optional
from pydantic import BaseModel


class ConversationCreate(BaseModel):
    workspace_id: int
    user_id: int
    persona_id: int
    title: Optional[str] = None


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    persona_id: Optional[int] = None


class ConversationResponse(BaseModel):
    id: int
    workspace_id: int
    user_id: int
    persona_id: int
    title: Optional[str] = None

    class Config:
        from_attributes = True