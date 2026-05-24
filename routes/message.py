from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.conversation import Conversation
from models.message import Message
from schemas.message import MessageCreate, MessageUpdate, MessageResponse
from services.message import (
    create_message,
    get_message_by_id,
    get_messages,
    update_message,
    delete_message,
)
from routes.dependencies import require_roles
from security.tenant import (
    ensure_conversation_access,
    ensure_personality_access,
    ensure_user_access,
    ensure_workspace_access,
)

router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
)


@router.post("/", response_model=MessageResponse)
def create_message_endpoint(
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    ensure_workspace_access(data.workspace_id, current_user)
    ensure_conversation_access(db, data.conversation_id, current_user)
    if data.sender_user_id is not None:
        ensure_user_access(db, data.sender_user_id, current_user)
    if data.sender_personality_id is not None:
        ensure_personality_access(db, data.sender_personality_id, current_user)
    return create_message(db, data)


@router.get("/", response_model=list[MessageResponse])
def list_messages_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return (
        db.query(Message)
        .join(Conversation)
        .filter(
            Message.workspace_id == current_user.workspace_id,
            Conversation.user_id == current_user.id,
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{message_id}", response_model=MessageResponse)
def get_message_endpoint(
    message_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_message_by_id(db, message_id)
    if (
        not db_obj
        or db_obj.workspace_id != current_user.workspace_id
        or db_obj.conversation.user_id != current_user.id
    ):
        raise HTTPException(status_code=404, detail="Message not found")
    return db_obj


@router.put("/{message_id}", response_model=MessageResponse)
def update_message_endpoint(
    message_id: int,
    data: MessageUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = get_message_by_id(db, message_id)
    if (
        not db_obj
        or db_obj.workspace_id != current_user.workspace_id
        or db_obj.conversation.user_id != current_user.id
    ):
        raise HTTPException(status_code=404, detail="Message not found")
    if data.workspace_id is not None:
        ensure_workspace_access(data.workspace_id, current_user)
    if data.conversation_id is not None:
        ensure_conversation_access(db, data.conversation_id, current_user)
    if data.sender_user_id is not None:
        ensure_user_access(db, data.sender_user_id, current_user)
    if data.sender_personality_id is not None:
        ensure_personality_access(db, data.sender_personality_id, current_user)
    db_obj = update_message(db, message_id, data)
    return db_obj


@router.delete("/{message_id}")
def delete_message_endpoint(
    message_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = get_message_by_id(db, message_id)
    if (
        not db_obj
        or db_obj.workspace_id != current_user.workspace_id
        or db_obj.conversation.user_id != current_user.id
    ):
        raise HTTPException(status_code=404, detail="Message not found")
    deleted = delete_message(db, message_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"message": "Message deleted successfully"}
