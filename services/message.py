from sqlalchemy.orm import Session
from models.message import Message
from schemas.message import MessageCreate, MessageUpdate


def create_message(db: Session, data: MessageCreate):
    message = Message(**data.dict(exclude_unset=True))
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_messages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Message).offset(skip).limit(limit).all()


def get_message_by_id(db: Session, message_id: int):
    return db.query(Message).filter(Message.id == message_id).first()


def get_messages_by_conversation_id(db: Session, conversation_id: int):
    return db.query(Message).filter(Message.conversation_id == conversation_id).all()


def get_messages_by_workspace_id(db: Session, workspace_id: int):
    return db.query(Message).filter(Message.workspace_id == workspace_id).all()


def update_message(db: Session, message_id: int, data: MessageUpdate):
    message = get_message_by_id(db, message_id)

    if not message:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(message, field, value)

    db.commit()
    db.refresh(message)
    return message


def delete_message(db: Session, message_id: int):
    message = get_message_by_id(db, message_id)

    if not message:
        return None

    db.delete(message)
    db.commit()
    return message