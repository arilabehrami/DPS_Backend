from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Message
from schemas.message import MessageCreate, MessageOut, MessageUpdate

router = APIRouter(prefix="/messages", tags=["Messages"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=MessageOut)
def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    new_msg = Message(
        content=message.content,
        role=message.role,
        conversation_id=message.conversation_id
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg

@router.get("/{message_id}", response_model=MessageOut)
def get_message(message_id: int, db: Session = Depends(get_db)):
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    return msg

@router.put("/{message_id}", response_model=MessageOut)
def update_message(message_id: int, message: MessageUpdate, db: Session = Depends(get_db)):
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")

    if message.content is not None:
        msg.content = message.content
    if message.role is not None:
        msg.role = message.role
    if message.conversation_id is not None:
        msg.conversation_id = message.conversation_id

    db.commit()
    db.refresh(msg)
    return msg


@router.delete("/{message_id}")
def delete_message(message_id: int, db: Session = Depends(get_db)):
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")

    db.delete(msg)
    db.commit()
    return {"detail": "Message deleted successfully"}
