from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class FeedbackBase(BaseModel):
    user_id: int
    conversation_id: int
    workspace_id: int
    rating: int
    comment: Optional[str] = None


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackUpdate(BaseModel):
    user_id: Optional[int] = None
    conversation_id: Optional[int] = None
    workspace_id: Optional[int] = None
    rating: Optional[int] = None
    comment: Optional[str] = None


class FeedbackResponse(FeedbackBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
