from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ExperimentBase(BaseModel):
    user_id: int
    workspace_id: int
    personality_id: Optional[int] = None
    conversation_id: Optional[int] = None
    title: str
    description: Optional[str] = None


class ExperimentCreate(ExperimentBase):
    pass


class ExperimentUpdate(BaseModel):
    user_id: Optional[int] = None
    workspace_id: Optional[int] = None
    personality_id: Optional[int] = None
    conversation_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None


class ExperimentResponse(ExperimentBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
