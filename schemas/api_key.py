from pydantic import BaseModel


class APIKeyCreate(BaseModel):
    user_id: int
    key: str