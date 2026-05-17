from pydantic import BaseModel


class PersonaBase(BaseModel):
    name: str
    description: str | None = None
    user_id: int


class PersonaCreate(PersonaBase):
    pass


class PersonaResponse(PersonaBase):
    id: int

    class Config:
        from_attributes = True