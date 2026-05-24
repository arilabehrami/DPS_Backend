from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PersonaTraitBase(BaseModel):
    personality_id: int
    trait_name: str
    trait_value: str


class PersonaTraitCreate(PersonaTraitBase):
    pass


class PersonaTraitUpdate(BaseModel):
    personality_id: Optional[int] = None
    trait_name: Optional[str] = None
    trait_value: Optional[str] = None


class PersonaTraitResponse(PersonaTraitBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
