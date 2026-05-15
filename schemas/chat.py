from pydantic import BaseModel


class ChatRequest(BaseModel):
    conversation_id: int
    message: str
    stream: bool = False


class ChatResponse(BaseModel):
    user_message: str
    ai_reply: str