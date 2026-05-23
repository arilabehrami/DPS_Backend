from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.conversation import Conversation
from models.user import User
from security.auth_security import get_current_user
from security.tenant import ensure_persona_access, ensure_user_access, ensure_workspace_access
from schemas.conversation import ConversationCreate, ConversationUpdate, ConversationResponse
from services.cache_service import get_or_set_list_cache, invalidate_cache_prefix
from services.conversation import (
    create_conversation,
    get_conversations,
    get_conversation_by_id,
    get_conversations_by_user_id,
    get_conversations_by_workspace_id,
    get_conversations_by_persona_id,
    update_conversation,
    delete_conversation
)

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=ConversationResponse)
def create_conversation_endpoint(
    data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_workspace_access(data.workspace_id, current_user)
    ensure_user_access(db, data.user_id, current_user)
    ensure_persona_access(db, data.persona_id, current_user)
    conversation = create_conversation(db, data)
    invalidate_cache_prefix("conversations:")
    return conversation


@router.get("/", response_model=list[ConversationResponse])
def get_conversations_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_or_set_list_cache(
        f"conversations:workspace:{current_user.workspace_id}:list:skip={skip}:limit={limit}",
        lambda: db.query(Conversation)
        .filter(Conversation.workspace_id == current_user.workspace_id)
        .offset(skip)
        .limit(limit)
        .all(),
        ConversationResponse,
    )


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation_endpoint(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .filter(Conversation.workspace_id == current_user.workspace_id)
        .first()
    )

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation


@router.get("/user/{user_id}", response_model=list[ConversationResponse])
def get_conversations_by_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_user_access(db, user_id, current_user)
    return get_or_set_list_cache(
        f"conversations:workspace:{current_user.workspace_id}:user:{user_id}",
        lambda: db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .filter(Conversation.workspace_id == current_user.workspace_id)
        .all(),
        ConversationResponse,
    )


@router.get("/workspace/{workspace_id}", response_model=list[ConversationResponse])
def get_conversations_by_workspace_endpoint(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_workspace_access(workspace_id, current_user)
    return get_or_set_list_cache(
        f"conversations:workspace:{current_user.workspace_id}",
        lambda: get_conversations_by_workspace_id(db, workspace_id),
        ConversationResponse,
    )


@router.get("/persona/{persona_id}", response_model=list[ConversationResponse])
def get_conversations_by_persona_endpoint(
    persona_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_persona_access(db, persona_id, current_user)
    return get_or_set_list_cache(
        f"conversations:workspace:{current_user.workspace_id}:persona:{persona_id}",
        lambda: db.query(Conversation)
        .filter(Conversation.persona_id == persona_id)
        .filter(Conversation.workspace_id == current_user.workspace_id)
        .all(),
        ConversationResponse,
    )


@router.put("/{conversation_id}", response_model=ConversationResponse)
def update_conversation_endpoint(
    conversation_id: int,
    data: ConversationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    ensure_workspace_access(conversation.workspace_id, current_user)
    if data.persona_id is not None:
        ensure_persona_access(db, data.persona_id, current_user)

    conversation = update_conversation(db, conversation_id, data)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    invalidate_cache_prefix("conversations:")
    return conversation


@router.delete("/{conversation_id}")
def delete_conversation_endpoint(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    ensure_workspace_access(conversation.workspace_id, current_user)
    conversation = delete_conversation(db, conversation_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    invalidate_cache_prefix("conversations:")
    return {"message": "Conversation deleted successfully"}
