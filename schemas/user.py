from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    full_name: str
    username: Optional[str] = None
    email: EmailStr
    workspace_id: int
    role_id: int


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    workspace_id: Optional[int] = None
    role_id: Optional[int] = None


class UserResponse(UserBase):
    id: int
    hashed_password: str
    last_rate: Optional[int] = None
    latest_rating: Optional[int] = None
    rating: Optional[int] = None
    lastRate: Optional[int] = None
    latestRating: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

