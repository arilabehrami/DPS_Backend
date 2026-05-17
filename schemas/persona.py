from typing import Optional
from pydantic import BaseModel


class PersonaCreate(BaseModel):
    workspace_id: int
    user_id: int
    name: Optional[str] = None
    description: Optional[str] = None


class PersonaUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class PersonaResponse(BaseModel):
    id: int
    workspace_id: int
    user_id: int
    name: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True