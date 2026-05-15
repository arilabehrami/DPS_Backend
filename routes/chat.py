from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models.conversation import Conversation
from models.message import Message
from schemas.chat import ChatRequest, ChatResponse
from services.ai_service import generate_ai_reply

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ChatResponse)
def chat(chat_data: ChatRequest, db: Session = Depends(get_db)):

    # 1. kontrollo conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == chat_data.conversation_id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

  
    user_message = Message(
        conversation_id=chat_data.conversation_id,
        sender="user",
        content=chat_data.message
    )

    db.add(user_message)
    db.commit()


    ai_reply = generate_ai_reply(chat_data.message)


    ai_message = Message(
        conversation_id=chat_data.conversation_id,
        sender="assistant",
        content=ai_reply
    )

    db.add(ai_message)
    db.commit()


    return ChatResponse(
        user_message=chat_data.message,
        ai_reply=ai_reply
    )