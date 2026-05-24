from typing import Optional
from pydantic import BaseModel


class ChatGenerateRequest(BaseModel):
    persona_id: int
    conversation_id: int
    message: str
    model: Optional[str] = None


class ChatGenerateResponse(BaseModel):
    user_message_id: int
    ai_message_id: int
    ai_response_id: int
    model_used: str
    response_text: str
    response: str
    message: str
    content: str


class ChatGenerateQueuedResponse(BaseModel):
    user_message_id: int
    status: str
    detail: str
