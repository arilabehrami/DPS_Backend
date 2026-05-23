from fastapi import APIRouter, Depends
from pydantic import BaseModel

from security.auth_security import get_current_user
from services.openai_service import chat_with_openai, analyze_text_with_openai

router = APIRouter(
    prefix="/openai",
    tags=["OpenAI AI"],
)


class ChatRequest(BaseModel):
    message: str
    model: str | None = None


class AnalyzeRequest(BaseModel):
    text: str
    model: str | None = None


@router.post("/chat")
def openai_chat(
    data: ChatRequest,
    current_user=Depends(get_current_user),
):
    response = chat_with_openai(data.message, data.model)
    return {"user_id": current_user.id, "response": response}


@router.post("/analyze")
def openai_analyze(
    data: AnalyzeRequest,
    current_user=Depends(get_current_user),
):
    analysis = analyze_text_with_openai(data.text, data.model)
    return {"user_id": current_user.id, "analysis": analysis}