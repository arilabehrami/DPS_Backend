from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class AIResponseCreate(BaseModel):
    message_id: Optional[int] = None
    response_text: str
    model_used: Optional[str] = None


class AIResponseUpdate(BaseModel):
    message_id: Optional[int] = None
    response_text: Optional[str] = None
    model_used: Optional[str] = None


class AIResponseResponse(BaseModel):
    id: int
    message_id: Optional[int] = None
    response_text: str
    model_used: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True