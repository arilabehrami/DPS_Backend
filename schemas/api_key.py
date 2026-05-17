from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class APIKeyCreate(BaseModel):
    user_id: Optional[int] = None
    key: Optional[str] = None


class APIKeyUpdate(BaseModel):
    key: Optional[str] = None


class APIKeyResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    key: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True