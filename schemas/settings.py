from pydantic import BaseModel


class SettingsCreate(BaseModel):
    user_id: int
    theme: str
    language: str


class SettingsResponse(BaseModel):
    id: int
    user_id: int
    theme: str
    language: str

    class Config:
        from_attributes = True