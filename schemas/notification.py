from pydantic import BaseModel


class NotificationCreate(BaseModel):
    user_id: int
    title: str


class NotificationOut(BaseModel):
    id: int
    user_id: int
    title: str
    is_read: bool

    class Config:
        from_attributes = True