from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models.conversation import Conversation
from models.message import Message
from schemas.conversation import ConversationCreate, ConversationOut
from schemas.message import MessageOut


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.post("/", response_model=ConversationOut)
def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db)
):
    new_conversation = Conversation(
        user_id=conversation.user_id,
        personality_id=conversation.personality_id,
        title=conversation.title
    )

    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)

    return new_conversation



@router.get("/", response_model=list[ConversationOut])
def get_user_conversations(
    user_id: int,
    db: Session = Depends(get_db)
):
    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .all()
    )

    return conversations



@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .all()
    )

    return messages