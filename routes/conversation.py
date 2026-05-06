from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Conversation
from schemas.conversation import ConversationCreate, ConversationOut, ConversationUpdate


router = APIRouter(prefix="/conversations", tags=["Conversations"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ConversationOut)
def create_conversation(conversation: ConversationCreate, db: Session = Depends(get_db)):
    new_conv = Conversation(
        user_id=conversation.user_id,
        personality_id=conversation.personality_id,
        title=getattr(conversation, "title", None),
        status=getattr(conversation, "status", None)
    )
    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)
    return new_conv


@router.get("/{conversation_id}", response_model=ConversationOut)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv

@router.put("/{conversation_id}", response_model=ConversationOut)
def update_conversation(conversation_id: int, conversation: ConversationUpdate, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.user_id is not None:
        conv.user_id = conversation.user_id
    if conversation.personality_id is not None:
        conv.personality_id = conversation.personality_id

    db.commit()
    db.refresh(conv)
    return conv


@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    db.delete(conv)
    db.commit()
    return {"detail": "Conversation deleted successfully"}

