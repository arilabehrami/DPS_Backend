from pydantic import BaseModel

class ConversationBase(BaseModel):
    user_id: int
    personality_id: int

class ConversationCreate(ConversationBase):
    title: str | None = None
    status: str | None = None


class ConversationUpdate(BaseModel):
    user_id: int | None = None
    personality_id: int | None = None
    title: str | None = None
    status: str | None = None


class ConversationOut(ConversationBase):
    id: int

    class Config:
        from_attributes = True

