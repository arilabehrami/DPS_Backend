from pydantic import BaseModel


class PersonaTraitCreate(BaseModel):
    personality_id: int
    trait_name: str


class PersonaTraitOut(BaseModel):
    id: int
    personality_id: int
    trait_name: str

    class Config:
        from_attributes = True