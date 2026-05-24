from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.conversation import Conversation
from schemas.conversation import ConversationCreate, ConversationUpdate, ConversationResponse
from services.conversation import (
    create_conversation,
    get_conversation_by_id,
    get_conversations,
    update_conversation,
    delete_conversation,
)
from routes.dependencies import require_roles
from security.tenant import ensure_personality_access, ensure_user_access, ensure_workspace_access

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.post("/", response_model=ConversationResponse)
def create_conversation_endpoint(
    data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    ensure_workspace_access(data.workspace_id, current_user)
    ensure_user_access(db, data.user_id, current_user)
    ensure_personality_access(db, data.personality_id, current_user)
    return create_conversation(db, data)


@router.get("/", response_model=list[ConversationResponse])
def list_conversations_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return (
        db.query(Conversation)
        .filter(
            Conversation.workspace_id == current_user.workspace_id,
            Conversation.user_id == current_user.id,
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation_endpoint(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_conversation_by_id(db, conversation_id)
    if (
        not db_obj
        or db_obj.workspace_id != current_user.workspace_id
        or db_obj.user_id != current_user.id
    ):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return db_obj


@router.put("/{conversation_id}", response_model=ConversationResponse)
def update_conversation_endpoint(
    conversation_id: int,
    data: ConversationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = get_conversation_by_id(db, conversation_id)
    if (
        not db_obj
        or db_obj.workspace_id != current_user.workspace_id
        or db_obj.user_id != current_user.id
    ):
        raise HTTPException(status_code=404, detail="Conversation not found")
    if data.workspace_id is not None:
        ensure_workspace_access(data.workspace_id, current_user)
    if data.user_id is not None:
        ensure_user_access(db, data.user_id, current_user)
    if data.personality_id is not None:
        ensure_personality_access(db, data.personality_id, current_user)
    db_obj = update_conversation(db, conversation_id, data)
    return db_obj


@router.delete("/{conversation_id}")
def delete_conversation_endpoint(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = get_conversation_by_id(db, conversation_id)
    if (
        not db_obj
        or db_obj.workspace_id != current_user.workspace_id
        or db_obj.user_id != current_user.id
    ):
        raise HTTPException(status_code=404, detail="Conversation not found")
    deleted = delete_conversation(db, conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation deleted successfully"}
