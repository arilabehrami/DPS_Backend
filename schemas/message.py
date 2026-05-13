from pydantic import BaseModel, ConfigDict

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

    model_config = ConfigDict(from_attributes=True)
