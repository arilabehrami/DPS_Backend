from pydantic import BaseModel


class ConversationBase(BaseModel):
    title: str
    user_id: int


class ConversationCreate(ConversationBase):
    pass


class ConversationResponse(ConversationBase):
    id: int

    class Config:
        from_attributes = True