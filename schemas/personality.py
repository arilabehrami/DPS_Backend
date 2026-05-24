from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PersonalityBase(BaseModel):
    persona_id: int
    user_id: Optional[int] = None
    workspace_id: int
    name: str
    description: Optional[str] = None


class PersonalityCreate(PersonalityBase):
    pass


class PersonalityUpdate(BaseModel):
    persona_id: Optional[int] = None
    user_id: Optional[int] = None
    workspace_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None


class PersonalityResponse(PersonalityBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
