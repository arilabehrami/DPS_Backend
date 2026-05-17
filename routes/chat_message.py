from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.message import Message
from schemas.chat_message import ChatMessageCreate, ChatMessageResponse

router = APIRouter(prefix="/chat-messages", tags=["ChatMessage"])


@router.post("/", response_model=ChatMessageResponse)
def create_message(msg: ChatMessageCreate, db: Session = Depends(get_db)):
    db_msg = Message(**msg.dict())
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return db_msg


@router.get("/")
def get_messages(db: Session = Depends(get_db)):
    return db.query(Message).all()