from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas.conversation import ConversationCreate, ConversationUpdate, ConversationResponse
from services.conversation import (
    create_conversation,
    get_conversation_by_id,
    get_conversations,
    update_conversation,
    delete_conversation,
)
from routes.dependencies import require_roles

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
    return create_conversation(db, data)


@router.get("/", response_model=list[ConversationResponse])
def list_conversations_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return get_conversations(db, skip=skip, limit=limit)


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation_endpoint(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_conversation_by_id(db, conversation_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return db_obj


@router.put("/{conversation_id}", response_model=ConversationResponse)
def update_conversation_endpoint(
    conversation_id: int,
    data: ConversationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = update_conversation(db, conversation_id, data)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return db_obj


@router.delete("/{conversation_id}")
def delete_conversation_endpoint(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    deleted = delete_conversation(db, conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation deleted successfully"}
