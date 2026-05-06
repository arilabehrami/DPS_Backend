from pydantic import BaseModel

class PersonalityBase(BaseModel):
    name: str
    description: str | None = None

class PersonalityCreate(PersonalityBase):
    user_id: int   # shto user_id që të lidhet me një User

class PersonalityUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    user_id: int | None = None   # opsionale në update

class PersonalityOut(PersonalityBase):
    id: int
    user_id: int   # shfaq edhe user_id në përgjigje

    class Config:
        orm_mode = True
