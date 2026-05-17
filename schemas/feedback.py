from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class FeedbackCreate(BaseModel):
    user_id: int
    message: str
    rating: Optional[int] = None


class FeedbackUpdate(BaseModel):
    message: Optional[str] = None
    rating: Optional[int] = None


class FeedbackResponse(BaseModel):
    id: int
    user_id: int
    message: str
    rating: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True