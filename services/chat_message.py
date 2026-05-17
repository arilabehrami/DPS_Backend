from sqlalchemy.orm import Session
from models.chat_message import ChatMessage
from schemas.chat_message import ChatMessageCreate, ChatMessageUpdate


def create_chat_message(db: Session, data: ChatMessageCreate):
    chat_message = ChatMessage(**data.dict(exclude_unset=True))
    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)
    return chat_message


def get_chat_messages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ChatMessage).offset(skip).limit(limit).all()


def get_chat_message_by_id(db: Session, chat_message_id: int):
    return db.query(ChatMessage).filter(ChatMessage.id == chat_message_id).first()


def get_chat_messages_by_conversation_id(db: Session, conversation_id: int):
    return db.query(ChatMessage).filter(ChatMessage.conversation_id == conversation_id).all()


def update_chat_message(db: Session, chat_message_id: int, data: ChatMessageUpdate):
    chat_message = get_chat_message_by_id(db, chat_message_id)

    if not chat_message:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(chat_message, field, value)

    db.commit()
    db.refresh(chat_message)
    return chat_message


def delete_chat_message(db: Session, chat_message_id: int):
    chat_message = get_chat_message_by_id(db, chat_message_id)

    if not chat_message:
        return None

    db.delete(chat_message)
    db.commit()
    return chat_message