from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.ai_response import AIResponse
from models.conversation import Conversation
from models.message import Message
from models.persona import Persona
from models.persona_trait import PersonaTrait
from models.user import User
from schemas.chat import (
    ChatGenerateQueuedResponse,
    ChatGenerateRequest,
    ChatGenerateResponse,
)
from security.auth_security import get_current_user
from services.background_jobs import generate_ai_response_job
from services.cache_service import invalidate_cache_prefix
from services.openai_service import chat_with_openai


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    dependencies=[Depends(get_current_user)],
)


def build_persona_prompt(persona: Persona, traits: list[PersonaTrait], message: str) -> str:
    trait_lines = "\n".join(
        f"- {trait.trait_name}: {trait.value}" if trait.value else f"- {trait.trait_name}"
        for trait in traits
    )

    return f"""
You are simulating a virtual persona in the Digital Personality Simulator.

Persona name: {persona.name or "Unnamed persona"}
Persona description: {persona.description or "No description provided"}
Persona traits:
{trait_lines or "- No traits provided"}

Respond naturally as this persona. Stay in character, be helpful, and keep the answer concise.

User message:
{message}
""".strip()


@router.post("/generate", response_model=ChatGenerateResponse)
def generate_chat_response(
    data: ChatGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    persona = db.query(Persona).filter(Persona.id == data.persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == data.conversation_id)
        .filter(Conversation.persona_id == data.persona_id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found for this persona")

    if persona.workspace_id != current_user.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Persona does not belong to your workspace",
        )

    if conversation.workspace_id != current_user.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conversation does not belong to your workspace",
        )

    traits = db.query(PersonaTrait).filter(PersonaTrait.persona_id == persona.id).all()
    prompt = build_persona_prompt(persona, traits, data.message)

    user_message = Message(
        workspace_id=current_user.workspace_id,
        conversation_id=conversation.id,
        sender="user",
        content=data.message,
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    invalidate_cache_prefix("messages:")

    try:
        response_text = chat_with_openai(prompt)
        model_used = data.model or "gpt-4o-mini"
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI response generation failed: {str(e)}",
        )

    ai_message = Message(
        workspace_id=current_user.workspace_id,
        conversation_id=conversation.id,
        sender="ai",
        content=response_text,
    )
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)
    invalidate_cache_prefix("messages:")

    ai_response = AIResponse(
        message_id=user_message.id,
        response_text=response_text,
        model_used=model_used,
    )
    db.add(ai_response)
    db.commit()
    db.refresh(ai_response)

    return ChatGenerateResponse(
        user_message_id=user_message.id,
        ai_message_id=ai_message.id,
        ai_response_id=ai_response.id,
        model_used=model_used,
        response_text=response_text,
    )


@router.post("/generate-background", response_model=ChatGenerateQueuedResponse)
def generate_chat_response_background(
    data: ChatGenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    persona = db.query(Persona).filter(Persona.id == data.persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == data.conversation_id)
        .filter(Conversation.persona_id == data.persona_id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found for this persona")

    if persona.workspace_id != current_user.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Persona does not belong to your workspace",
        )

    if conversation.workspace_id != current_user.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conversation does not belong to your workspace",
        )

    traits = db.query(PersonaTrait).filter(PersonaTrait.persona_id == persona.id).all()
    prompt = build_persona_prompt(persona, traits, data.message)

    user_message = Message(
        workspace_id=current_user.workspace_id,
        conversation_id=conversation.id,
        sender="user",
        content=data.message,
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    invalidate_cache_prefix("messages:")

    background_tasks.add_task(
        generate_ai_response_job,
        current_user.id,
        current_user.workspace_id,
        conversation.id,
        user_message.id,
        prompt,
        data.model,
    )

    return ChatGenerateQueuedResponse(
        user_message_id=user_message.id,
        status="queued",
        detail="AI response generation started in the background",
    )