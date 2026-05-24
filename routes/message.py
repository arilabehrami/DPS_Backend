from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas.message import MessageCreate, MessageUpdate, MessageResponse
from services.message import (
    create_message,
    get_message_by_id,
    get_messages,
    update_message,
    delete_message,
)
from routes.dependencies import require_roles

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
    return create_message(db, data)


@router.get("/", response_model=list[MessageResponse])
def list_messages_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return get_messages(db, skip=skip, limit=limit)


@router.get("/{message_id}", response_model=MessageResponse)
def get_message_endpoint(
    message_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_message_by_id(db, message_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Message not found")
    return db_obj


@router.put("/{message_id}", response_model=MessageResponse)
def update_message_endpoint(
    message_id: int,
    data: MessageUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = update_message(db, message_id, data)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Message not found")
    return db_obj


@router.delete("/{message_id}")
def delete_message_endpoint(
    message_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    deleted = delete_message(db, message_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"message": "Message deleted successfully"}
