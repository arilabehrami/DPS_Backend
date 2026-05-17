from typing import Optional
from pydantic import BaseModel


class PersonaTraitCreate(BaseModel):
    persona_id: Optional[int] = None
    trait_name: str
    value: Optional[str] = None


class PersonaTraitUpdate(BaseModel):
    trait_name: Optional[str] = None
    value: Optional[str] = None


class PersonaTraitResponse(BaseModel):
    id: int
    persona_id: Optional[int] = None
    trait_name: str
    value: Optional[str] = None

    class Config:
        from_attributes = True