from pydantic import BaseModel
from datetime import datetime


class SessionCreate(BaseModel):
    user_id: int
    token: str


class SessionOut(BaseModel):
    id: int
    user_id: int
    token: str
    created_at: datetime

    class Config:
        from_attributes = True