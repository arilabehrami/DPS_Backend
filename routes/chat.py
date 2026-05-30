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
    response_language: str | None = "en"


class ChatGenerateResponse(BaseModel):
    conversation_id: int
    persona_id: int
    response: str
    message: str


def ensure_default_persona(db: Session, current_user) -> Persona:
    persona = (
        db.query(Persona)
        .filter(Persona.workspace_id == current_user.workspace_id)
        .order_by(Persona.id.asc())
        .first()
    )
    if persona:
        return persona

    persona = Persona(
        name="Aura",
        description="Friendly assistant persona for chatting and guidance.",
        workspace_id=current_user.workspace_id,
        user_id=current_user.id,
    )
    db.add(persona)
    db.commit()
    db.refresh(persona)
    return persona


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


LANGUAGE_NAMES = {
    "en": "English",
    "sq": "Albanian",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
}

UNREACHABLE_MESSAGES = {
    "en": "Ollama AI service is not reachable. Start Ollama with `ollama run phi3`. Your message was: {message}",
    "sq": "Sherbimi Ollama AI nuk eshte i arritshem. Nise Ollama me `ollama run phi3`. Mesazhi yt ishte: {message}",
    "es": "El servicio Ollama AI no esta disponible. Inicia Ollama con `ollama run phi3`. Tu mensaje fue: {message}",
    "fr": "Le service Ollama AI n'est pas disponible. Lancez Ollama avec `ollama run phi3`. Votre message etait : {message}",
    "de": "Der Ollama AI-Dienst ist nicht erreichbar. Starte Ollama mit `ollama run phi3`. Deine Nachricht war: {message}",
}


def normalize_language(language: str | None) -> str:
    return language if language in LANGUAGE_NAMES else "en"


@router.post("/generate", response_model=ChatGenerateResponse)
def generate_chat_response(
    data: ChatGenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "employee", "client")),
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
        # Fallback for frontend defaults (persona_id=1) and empty workspaces.
        persona = ensure_default_persona(db, current_user)

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

    response_language = normalize_language(data.response_language)
    language_name = LANGUAGE_NAMES[response_language]
    system_prompt = (
        f"You are {persona.name}, a helpful digital personality. "
        f"Always answer naturally and clearly in {language_name}. "
        "If the user writes in another language, still reply in the selected response language."
    )
    cache_key = f"chat:v3:{current_user.workspace_id}:{current_user.id}:{personality.id}:{response_language}:{data.model or 'default'}:{data.message}"
    cached = cache_service.get(cache_key)
    if cached:
        ai_text = cached["response"]
    else:
        ai_text = llm_service.generate(data.message, system_prompt, data.model)
        is_unreachable = llm_service.is_unreachable_response(ai_text)
        if is_unreachable:
            ai_text = UNREACHABLE_MESSAGES[response_language].format(message=data.message)
        if not is_unreachable:
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
