from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.conversation import Conversation
from schemas.conversation import (
    ConversationCreate,
    ConversationResponse
)

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"]
)


@router.post("/", response_model=ConversationResponse)
def create_conversation(
    conversation_data: ConversationCreate,
    db: Session = Depends(get_db)
):
    conversation = Conversation(**conversation_data.model_dump())

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


@router.get("/", response_model=list[ConversationResponse])
def get_conversations(db: Session = Depends(get_db)):
    return db.query(Conversation).all()