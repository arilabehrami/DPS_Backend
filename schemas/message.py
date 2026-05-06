from pydantic import BaseModel

class MessageBase(BaseModel):
    content: str
    role: str
    conversation_id: int

class MessageCreate(MessageBase):
    pass

class MessageUpdate(BaseModel):
    content: str | None = None
    role: str | None = None
    conversation_id: int | None = None

class MessageOut(MessageBase):
    id: int

    class Config:
        orm_mode = True
