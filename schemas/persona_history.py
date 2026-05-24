from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PersonaHistoryBase(BaseModel):
    personality_id: int
    change_description: str


class PersonaHistoryCreate(PersonaHistoryBase):
    pass


class PersonaHistoryUpdate(BaseModel):
    personality_id: Optional[int] = None
    change_description: Optional[str] = None


class PersonaHistoryResponse(PersonaHistoryBase):
    id: int
    changed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
