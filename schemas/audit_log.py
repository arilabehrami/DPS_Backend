from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class AuditLogCreate(BaseModel):
    action: Optional[str] = None


class AuditLogUpdate(BaseModel):
    action: Optional[str] = None


class AuditLogResponse(BaseModel):
    id: int
    action: Optional[str] = None
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True