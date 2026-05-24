from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SettingBase(BaseModel):
    scope: str
    key: str
    value: str
    workspace_id: Optional[int] = None
    user_id: Optional[int] = None


class SettingCreate(SettingBase):
    pass


class SettingUpdate(BaseModel):
    scope: Optional[str] = None
    key: Optional[str] = None
    value: Optional[str] = None
    workspace_id: Optional[int] = None
    user_id: Optional[int] = None


class SettingResponse(SettingBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
