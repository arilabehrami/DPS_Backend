from sqlalchemy.orm import Session
from models.conversation import Conversation
from schemas.conversation import ConversationCreate, ConversationUpdate


def create_conversation(db: Session, data: ConversationCreate) -> Conversation:
    db_obj = Conversation(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_conversation_by_id(db: Session, conversation_id: int) -> Conversation | None:
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()


def get_conversations(db: Session, skip: int = 0, limit: int = 100) -> list[Conversation]:
    return db.query(Conversation).offset(skip).limit(limit).all()


def update_conversation(db: Session, conversation_id: int, data: ConversationUpdate) -> Conversation | None:
    db_obj = get_conversation_by_id(db, conversation_id)
    if not db_obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_conversation(db: Session, conversation_id: int) -> bool:
    db_obj = get_conversation_by_id(db, conversation_id)
    if not db_obj:
        return False

    db.delete(db_obj)
    db.commit()
    return True
