from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.message import MessageCreate, MessageUpdate, MessageResponse
from services.message import (
    create_message,
    get_messages,
    get_message_by_id,
    get_messages_by_conversation_id,
    get_messages_by_workspace_id,
    update_message,
    delete_message
)

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post("/", response_model=MessageResponse)
def create_message_endpoint(data: MessageCreate, db: Session = Depends(get_db)):
    return create_message(db, data)


@router.get("/", response_model=list[MessageResponse])
def get_messages_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_messages(db, skip, limit)


@router.get("/{message_id}", response_model=MessageResponse)
def get_message_endpoint(message_id: int, db: Session = Depends(get_db)):
    message = get_message_by_id(db, message_id)

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    return message


@router.get("/conversation/{conversation_id}", response_model=list[MessageResponse])
def get_messages_by_conversation_endpoint(conversation_id: int, db: Session = Depends(get_db)):
    return get_messages_by_conversation_id(db, conversation_id)


@router.get("/workspace/{workspace_id}", response_model=list[MessageResponse])
def get_messages_by_workspace_endpoint(workspace_id: int, db: Session = Depends(get_db)):
    return get_messages_by_workspace_id(db, workspace_id)


@router.put("/{message_id}", response_model=MessageResponse)
def update_message_endpoint(message_id: int, data: MessageUpdate, db: Session = Depends(get_db)):
    message = update_message(db, message_id, data)

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    return message


@router.delete("/{message_id}")
def delete_message_endpoint(message_id: int, db: Session = Depends(get_db)):
    message = delete_message(db, message_id)

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    return {"message": "Message deleted successfully"}