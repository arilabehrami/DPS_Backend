from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AuditLogBase(BaseModel):
    user_id: int
    workspace_id: Optional[int] = None
    action: str


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogUpdate(BaseModel):
    user_id: Optional[int] = None
    workspace_id: Optional[int] = None
    action: Optional[str] = None


class AuditLogResponse(AuditLogBase):
    id: int
    timestamp: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
