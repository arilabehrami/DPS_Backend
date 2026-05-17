from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class PersonaHistoryCreate(BaseModel):
    persona_id: int
    changed_field: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None


class PersonaHistoryUpdate(BaseModel):
    changed_field: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None


class PersonaHistoryResponse(BaseModel):
    id: int
    persona_id: int
    changed_field: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_at: Optional[datetime] = None

    class Config:
        from_attributes = True