from sqlalchemy.orm import Session
from models.session import Session
from schemas.session import SessionCreate, SessionUpdate


def create_session(db: Session, data: SessionCreate) -> Session:
    db_obj = Session(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_session_by_id(db: Session, session_id: int) -> Session | None:
    return db.query(Session).filter(Session.id == session_id).first()


def get_sessions(db: Session, skip: int = 0, limit: int = 100) -> list[Session]:
    return db.query(Session).offset(skip).limit(limit).all()


def update_session(db: Session, session_id: int, data: SessionUpdate) -> Session | None:
    db_obj = get_session_by_id(db, session_id)
    if not db_obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_session(db: Session, session_id: int) -> bool:
    db_obj = get_session_by_id(db, session_id)
    if not db_obj:
        return False

    db.delete(db_obj)
    db.commit()
    return True
