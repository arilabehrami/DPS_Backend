from sqlalchemy.orm import Session
from models.conversation import Conversation
from schemas.conversation import ConversationCreate, ConversationUpdate


def create_conversation(db: Session, data: ConversationCreate):
    conversation = Conversation(**data.dict(exclude_unset=True))
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_conversations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Conversation).offset(skip).limit(limit).all()


def get_conversation_by_id(db: Session, conversation_id: int):
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()


def get_conversations_by_user_id(db: Session, user_id: int):
    return db.query(Conversation).filter(Conversation.user_id == user_id).all()


def get_conversations_by_workspace_id(db: Session, workspace_id: int):
    return db.query(Conversation).filter(Conversation.workspace_id == workspace_id).all()


def get_conversations_by_persona_id(db: Session, persona_id: int):
    return db.query(Conversation).filter(Conversation.persona_id == persona_id).all()


def update_conversation(db: Session, conversation_id: int, data: ConversationUpdate):
    conversation = get_conversation_by_id(db, conversation_id)

    if not conversation:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(conversation, field, value)

    db.commit()
    db.refresh(conversation)
    return conversation


def delete_conversation(db: Session, conversation_id: int):
    conversation = get_conversation_by_id(db, conversation_id)

    if not conversation:
        return None

    db.delete(conversation)
    db.commit()
    return conversation