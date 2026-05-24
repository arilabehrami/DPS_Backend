from sqlalchemy.orm import Session
from models.message import Message
from schemas.message import MessageCreate, MessageUpdate


def create_message(db: Session, data: MessageCreate) -> Message:
    db_obj = Message(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_message_by_id(db: Session, message_id: int) -> Message | None:
    return db.query(Message).filter(Message.id == message_id).first()


def get_messages(db: Session, skip: int = 0, limit: int = 100) -> list[Message]:
    return db.query(Message).offset(skip).limit(limit).all()


def update_message(db: Session, message_id: int, data: MessageUpdate) -> Message | None:
    db_obj = get_message_by_id(db, message_id)
    if not db_obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_message(db: Session, message_id: int) -> bool:
    db_obj = get_message_by_id(db, message_id)
    if not db_obj:
        return False

    db.delete(db_obj)
    db.commit()
    return True
