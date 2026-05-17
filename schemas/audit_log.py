from pydantic import BaseModel
from datetime import datetime


class AuditLogCreate(BaseModel):
    user_id: int
    action: str


class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    created_at: datetime

    class Config:
        from_attributes = True