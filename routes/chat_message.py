from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.chat_message import ChatMessage
from models.conversation import Conversation
from models.user import User
from security.auth_security import get_current_user
from security.tenant import ensure_conversation_access
from schemas.chat_message import ChatMessageCreate, ChatMessageUpdate, ChatMessageResponse
from services.chat_message import (
    create_chat_message,
    get_chat_messages,
    get_chat_message_by_id,
    get_chat_messages_by_conversation_id,
    update_chat_message,
    delete_chat_message
)

router = APIRouter(
    prefix="/chat-messages",
    tags=["Chat Messages"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=ChatMessageResponse)
def create_chat_message_endpoint(
    data: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.conversation_id is not None:
        ensure_conversation_access(db, data.conversation_id, current_user)
    return create_chat_message(db, data)


@router.get("/", response_model=list[ChatMessageResponse])
def get_chat_messages_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(ChatMessage)
        .join(Conversation, ChatMessage.conversation_id == Conversation.id)
        .filter(Conversation.workspace_id == current_user.workspace_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{chat_message_id}", response_model=ChatMessageResponse)
def get_chat_message_endpoint(
    chat_message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chat_message = get_chat_message_by_id(db, chat_message_id)

    if not chat_message:
        raise HTTPException(status_code=404, detail="Chat message not found")

    if chat_message.conversation_id is not None:
        ensure_conversation_access(db, chat_message.conversation_id, current_user)

    return chat_message


@router.get("/conversation/{conversation_id}", response_model=list[ChatMessageResponse])
def get_chat_messages_by_conversation_endpoint(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_conversation_access(db, conversation_id, current_user)
    return get_chat_messages_by_conversation_id(db, conversation_id)


@router.put("/{chat_message_id}", response_model=ChatMessageResponse)
def update_chat_message_endpoint(
    chat_message_id: int,
    data: ChatMessageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chat_message = get_chat_message_by_id(db, chat_message_id)
    if not chat_message:
        raise HTTPException(status_code=404, detail="Chat message not found")

    if chat_message.conversation_id is not None:
        ensure_conversation_access(db, chat_message.conversation_id, current_user)

    chat_message = update_chat_message(db, chat_message_id, data)

    if not chat_message:
        raise HTTPException(status_code=404, detail="Chat message not found")

    return chat_message


@router.delete("/{chat_message_id}")
def delete_chat_message_endpoint(
    chat_message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chat_message = get_chat_message_by_id(db, chat_message_id)
    if not chat_message:
        raise HTTPException(status_code=404, detail="Chat message not found")

    if chat_message.conversation_id is not None:
        ensure_conversation_access(db, chat_message.conversation_id, current_user)

    chat_message = delete_chat_message(db, chat_message_id)

    if not chat_message:
        raise HTTPException(status_code=404, detail="Chat message not found")

    return {"message": "Chat message deleted successfully"}
