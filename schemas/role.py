from typing import Optional
from pydantic import BaseModel


class RoleCreate(BaseModel):
    name: Optional[str] = None


class RoleUpdate(BaseModel):
    name: Optional[str] = None


class RoleResponse(BaseModel):
    id: int
    name: Optional[str] = None

    class Config:
        from_attributes = True