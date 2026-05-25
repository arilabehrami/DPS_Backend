from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class RatingBase(BaseModel):
    user_id: int
    personality_id: Optional[int] = None
    conversation_id: Optional[int] = None
    workspace_id: int
    score: int
    comment: Optional[str] = None


class RatingCreate(RatingBase):
    pass


class RatingUpdate(BaseModel):
    user_id: Optional[int] = None
    personality_id: Optional[int] = None
    conversation_id: Optional[int] = None
    workspace_id: Optional[int] = None
    score: Optional[int] = None
    comment: Optional[str] = None


class RatingResponse(RatingBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
