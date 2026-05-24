from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.conversation import Conversation
from models.message import Message
from models.persona import Persona
from models.personality import Personality
from routes.dependencies import require_roles
from services.background_jobs import record_event_log
from services.cache import cache_service
from services.llm_service import llm_service

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


def get_or_create_personality(
    db: Session,
    persona: Persona,
    user_id: int,
    workspace_id: int,
) -> Personality:
    personality = (
        db.query(Personality)
        .filter(
            Personality.persona_id == persona.id,
            Personality.workspace_id == workspace_id,
        )
        .first()
    )
    if personality:
        return personality

    personality = Personality(
        persona_id=persona.id,
        user_id=user_id,
        workspace_id=workspace_id,
        name=persona.name,
        description=persona.description,
    )
    db.add(personality)
    db.commit()
    db.refresh(personality)
    return personality


@router.post("/generate", response_model=ChatGenerateResponse)
def generate_chat_response(
    data: ChatGenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    if not data.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    persona = (
        db.query(Persona)
        .filter(
            Persona.id == data.persona_id,
            Persona.workspace_id == current_user.workspace_id,
        )
        .first()
    )
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    personality = get_or_create_personality(
        db,
        persona,
        current_user.id,
        current_user.workspace_id,
    )

    conversation = None
    if data.conversation_id:
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == data.conversation_id,
                Conversation.workspace_id == current_user.workspace_id,
                Conversation.user_id == current_user.id,
            )
            .first()
        )

    if not conversation:
        conversation = Conversation(
            user_id=current_user.id,
            personality_id=personality.id,
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

    system_prompt = (
        f"You are {persona.name}, a helpful digital personality. "
        "Answer naturally and clearly in the same language as the user unless asked otherwise."
    )
    cache_key = f"chat:{current_user.workspace_id}:{current_user.id}:{personality.id}:{data.model or 'default'}:{data.message}"
    cached = cache_service.get(cache_key)
    if cached:
        ai_text = cached["response"]
    else:
        ai_text = llm_service.generate(data.message, system_prompt, data.model)
        cache_service.set(cache_key, {"response": ai_text}, ttl_seconds=300)

    ai_msg = Message(
        conversation_id=conversation.id,
        workspace_id=current_user.workspace_id,
        sender_type="personality",
        sender_personality_id=personality.id,
        content=ai_text,
    )
    conversation.updated_at = datetime.now(timezone.utc)
    db.add(ai_msg)
    db.commit()

    background_tasks.add_task(
        record_event_log,
        current_user.id,
        current_user.workspace_id,
        "chat_generate",
        data.message[:255],
    )

    return ChatGenerateResponse(
        conversation_id=conversation.id,
        persona_id=data.persona_id,
        response=ai_text,
        message=ai_text,
    )
