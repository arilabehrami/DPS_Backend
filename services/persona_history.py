from sqlalchemy.orm import Session
from models.persona_history import PersonaHistory
from schemas.persona_history import PersonaHistoryCreate, PersonaHistoryUpdate


def create_persona_history(db: Session, data: PersonaHistoryCreate) -> PersonaHistory:
    db_obj = PersonaHistory(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_persona_history_by_id(db: Session, persona_history_id: int) -> PersonaHistory | None:
    return db.query(PersonaHistory).filter(PersonaHistory.id == persona_history_id).first()


def get_persona_historys(db: Session, skip: int = 0, limit: int = 100) -> list[PersonaHistory]:
    return db.query(PersonaHistory).offset(skip).limit(limit).all()


def update_persona_history(db: Session, persona_history_id: int, data: PersonaHistoryUpdate) -> PersonaHistory | None:
    db_obj = get_persona_history_by_id(db, persona_history_id)
    if not db_obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_persona_history(db: Session, persona_history_id: int) -> bool:
    db_obj = get_persona_history_by_id(db, persona_history_id)
    if not db_obj:
        return False

    db.delete(db_obj)
    db.commit()
    return True
