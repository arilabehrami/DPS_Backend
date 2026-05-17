from typing import Optional
from pydantic import BaseModel


class PersonalityCreate(BaseModel):
    workspace_id: int
    name: str
    description: Optional[str] = None
    user_id: Optional[int] = None


class PersonalityUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class PersonalityResponse(BaseModel):
    id: int
    workspace_id: int
    name: str
    description: Optional[str] = None
    user_id: Optional[int] = None

    class Config:
        from_attributes = True