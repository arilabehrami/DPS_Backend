from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.conversation import ConversationCreate, ConversationUpdate, ConversationResponse
from services.conversation import (
    create_conversation,
    get_conversations,
    get_conversation_by_id,
    get_conversations_by_user_id,
    get_conversations_by_workspace_id,
    get_conversations_by_persona_id,
    update_conversation,
    delete_conversation
)

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.post("/", response_model=ConversationResponse)
def create_conversation_endpoint(data: ConversationCreate, db: Session = Depends(get_db)):
    return create_conversation(db, data)


@router.get("/", response_model=list[ConversationResponse])
def get_conversations_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_conversations(db, skip, limit)


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation_endpoint(conversation_id: int, db: Session = Depends(get_db)):
    conversation = get_conversation_by_id(db, conversation_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation


@router.get("/user/{user_id}", response_model=list[ConversationResponse])
def get_conversations_by_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    return get_conversations_by_user_id(db, user_id)


@router.get("/workspace/{workspace_id}", response_model=list[ConversationResponse])
def get_conversations_by_workspace_endpoint(workspace_id: int, db: Session = Depends(get_db)):
    return get_conversations_by_workspace_id(db, workspace_id)


@router.get("/persona/{persona_id}", response_model=list[ConversationResponse])
def get_conversations_by_persona_endpoint(persona_id: int, db: Session = Depends(get_db)):
    return get_conversations_by_persona_id(db, persona_id)


@router.put("/{conversation_id}", response_model=ConversationResponse)
def update_conversation_endpoint(conversation_id: int, data: ConversationUpdate, db: Session = Depends(get_db)):
    conversation = update_conversation(db, conversation_id, data)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation


@router.delete("/{conversation_id}")
def delete_conversation_endpoint(conversation_id: int, db: Session = Depends(get_db)):
    conversation = delete_conversation(db, conversation_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"message": "Conversation deleted successfully"}