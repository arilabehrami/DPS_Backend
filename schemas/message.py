from pydantic import BaseModel


class MessageBase(BaseModel):
    content: str
    conversation_id: int


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id: int

    class Config:
        from_attributes = True