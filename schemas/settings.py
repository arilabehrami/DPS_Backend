from typing import Optional
from pydantic import BaseModel


class SettingsCreate(BaseModel):
    user_id: Optional[int] = None
    preferences: Optional[dict] = None


class SettingsUpdate(BaseModel):
    preferences: Optional[dict] = None


class SettingsResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    preferences: Optional[dict] = None

    class Config:
        from_attributes = True