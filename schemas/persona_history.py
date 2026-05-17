from pydantic import BaseModel
from datetime import datetime


class PersonaHistoryCreate(BaseModel):
    persona_id: int
    event: str


class PersonaHistoryResponse(BaseModel):
    id: int
    persona_id: int
    event: str
    created_at: datetime

    class Config:
        from_attributes = True