from sqlalchemy.orm import Session
from models.persona_history import PersonaHistory
from schemas.persona_history import PersonaHistoryCreate, PersonaHistoryUpdate


def create_persona_history(db: Session, data: PersonaHistoryCreate):
    persona_history = PersonaHistory(**data.dict(exclude_unset=True))
    db.add(persona_history)
    db.commit()
    db.refresh(persona_history)
    return persona_history


def get_persona_history(db: Session, skip: int = 0, limit: int = 100):
    return db.query(PersonaHistory).offset(skip).limit(limit).all()


def get_persona_history_by_id(db: Session, history_id: int):
    return db.query(PersonaHistory).filter(PersonaHistory.id == history_id).first()


def get_persona_history_by_persona_id(db: Session, persona_id: int):
    return db.query(PersonaHistory).filter(PersonaHistory.persona_id == persona_id).all()


def update_persona_history(db: Session, history_id: int, data: PersonaHistoryUpdate):
    persona_history = get_persona_history_by_id(db, history_id)

    if not persona_history:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(persona_history, field, value)

    db.commit()
    db.refresh(persona_history)
    return persona_history


def delete_persona_history(db: Session, history_id: int):
    persona_history = get_persona_history_by_id(db, history_id)

    if not persona_history:
        return None

    db.delete(persona_history)
    db.commit()
    return persona_history