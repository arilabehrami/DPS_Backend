from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ApiKeyBase(BaseModel):
    user_id: int
    key_hash: str


class ApiKeyCreate(ApiKeyBase):
    pass


class ApiKeyUpdate(BaseModel):
    user_id: Optional[int] = None
    key_hash: Optional[str] = None


class ApiKeyResponse(ApiKeyBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
