from typing import Optional
from pydantic import BaseModel


class MessageCreate(BaseModel):
    workspace_id: int
    conversation_id: int
    sender: Optional[str] = None
    content: Optional[str] = None


class MessageUpdate(BaseModel):
    sender: Optional[str] = None
    content: Optional[str] = None


class MessageResponse(BaseModel):
    id: int
    workspace_id: int
    conversation_id: int
    sender: Optional[str] = None
    content: Optional[str] = None

    class Config:
        from_attributes = True