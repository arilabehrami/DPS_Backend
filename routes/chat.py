from datetime import datetime, timezone
import os

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.conversation import Conversation
from models.message import Message
from models.persona import Persona
from routes.dependencies import require_roles

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatGenerateRequest(BaseModel):
    persona_id: int = 1
    conversation_id: int | None = None
    message: str
    model: str | None = None


class ChatGenerateResponse(BaseModel):
    conversation_id: int
    persona_id: int
    response: str
    message: str


def local_ai_response(user_message: str, persona: Persona | None) -> str:
    persona_name = persona.name if persona else "Aura"
    return (
        f"{persona_name}: E pranova mesazhin tënd. "
        f"Për demo pa pagesë/OpenAI key, përgjigjja po gjenerohet lokalisht për tekstin: {user_message}"
    )


@router.post("/generate", response_model=ChatGenerateResponse)
def generate_chat_response(
    data: ChatGenerateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    if not data.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    persona = db.query(Persona).filter(Persona.id == data.persona_id).first()

    conversation = None
    if data.conversation_id:
        conversation = db.query(Conversation).filter(Conversation.id == data.conversation_id).first()

    if not conversation:
        conversation = Conversation(
            user_id=current_user.id,
            personality_id=data.persona_id,
            workspace_id=current_user.workspace_id,
            title=data.message[:80],
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    user_msg = Message(
        conversation_id=conversation.id,
        workspace_id=current_user.workspace_id,
        sender_type="user",
        sender_user_id=current_user.id,
        content=data.message,
    )
    db.add(user_msg)

    # Nëse vendos OPENAI_API_KEY në .env, këtu mund ta zëvendësosh local_ai_response me thirrje reale.
    ai_text = local_ai_response(data.message, persona)

    ai_msg = Message(
        conversation_id=conversation.id,
        workspace_id=current_user.workspace_id,
        sender_type="personality",
        sender_personality_id=data.persona_id,
        content=ai_text,
    )
    conversation.updated_at = datetime.now(timezone.utc)
    db.add(ai_msg)
    db.commit()

    return ChatGenerateResponse(
        conversation_id=conversation.id,
        persona_id=data.persona_id,
        response=ai_text,
        message=ai_text,
    )
