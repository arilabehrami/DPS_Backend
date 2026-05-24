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
    email: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = "persona"
    status: Optional[str] = "active"

    class Config:
        from_attributes = True
