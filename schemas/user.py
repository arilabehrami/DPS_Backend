from typing import Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    workspace_id: int
    role_id: int
    username: str
    email: str
    password: str


class UserUpdate(BaseModel):
    workspace_id: Optional[int] = None
    role_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    workspace_id: int
    role_id: int
    username: str
    email: str

    class Config:
        from_attributes = True
