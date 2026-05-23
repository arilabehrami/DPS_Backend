from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.message import Message
from models.user import User
from security.auth_security import get_current_user
from security.tenant import ensure_conversation_access, ensure_workspace_access
from schemas.message import MessageCreate, MessageUpdate, MessageResponse
from services.cache_service import get_or_set_list_cache, invalidate_cache_prefix
from services.message import (
    create_message,
    get_messages,
    get_message_by_id,
    get_messages_by_conversation_id,
    get_messages_by_workspace_id,
    update_message,
    delete_message
)

router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=MessageResponse)
def create_message_endpoint(
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_workspace_access(data.workspace_id, current_user)
    ensure_conversation_access(db, data.conversation_id, current_user)
    message = create_message(db, data)
    invalidate_cache_prefix("messages:")
    return message


@router.get("/", response_model=list[MessageResponse])
def get_messages_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_or_set_list_cache(
        f"messages:workspace:{current_user.workspace_id}:list:skip={skip}:limit={limit}",
        lambda: db.query(Message)
        .filter(Message.workspace_id == current_user.workspace_id)
        .offset(skip)
        .limit(limit)
        .all(),
        MessageResponse,
    )


@router.get("/{message_id}", response_model=MessageResponse)
def get_message_endpoint(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    message = (
        db.query(Message)
        .filter(Message.id == message_id)
        .filter(Message.workspace_id == current_user.workspace_id)
        .first()
    )

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    return message


@router.get("/conversation/{conversation_id}", response_model=list[MessageResponse])
def get_messages_by_conversation_endpoint(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_conversation_access(db, conversation_id, current_user)
    return get_or_set_list_cache(
        f"messages:workspace:{current_user.workspace_id}:conversation:{conversation_id}",
        lambda: db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .filter(Message.workspace_id == current_user.workspace_id)
        .all(),
        MessageResponse,
    )


@router.get("/workspace/{workspace_id}", response_model=list[MessageResponse])
def get_messages_by_workspace_endpoint(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_workspace_access(workspace_id, current_user)
    return get_or_set_list_cache(
        f"messages:workspace:{current_user.workspace_id}",
        lambda: get_messages_by_workspace_id(db, workspace_id),
        MessageResponse,
    )


@router.put("/{message_id}", response_model=MessageResponse)
def update_message_endpoint(
    message_id: int,
    data: MessageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    message = get_message_by_id(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    ensure_workspace_access(message.workspace_id, current_user)
    message = update_message(db, message_id, data)

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    invalidate_cache_prefix("messages:")
    return message


@router.delete("/{message_id}")
def delete_message_endpoint(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    message = get_message_by_id(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    ensure_workspace_access(message.workspace_id, current_user)
    message = delete_message(db, message_id)

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    invalidate_cache_prefix("messages:")
    return {"message": "Message deleted successfully"}
