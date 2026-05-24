from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PersonaBase(BaseModel):
    name: str
    description: Optional[str] = None
    workspace_id: int
    user_id: Optional[int] = None


class PersonaCreate(PersonaBase):
    pass


class PersonaUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    workspace_id: Optional[int] = None
    user_id: Optional[int] = None


class PersonaResponse(PersonaBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
