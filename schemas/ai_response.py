from pydantic import BaseModel


class AIResponseCreate(BaseModel):
    conversation_id: int
    response: str


class AIResponseOut(BaseModel):
    id: int
    conversation_id: int
    response: str

    class Config:
        from_attributes = True