from sqlalchemy.orm import Session
from models.persona import Persona
from schemas.persona import PersonaCreate, PersonaUpdate


def create_persona(db: Session, data: PersonaCreate) -> Persona:
    db_obj = Persona(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_persona_by_id(db: Session, persona_id: int) -> Persona | None:
    return db.query(Persona).filter(Persona.id == persona_id).first()


def get_personas(db: Session, skip: int = 0, limit: int = 100) -> list[Persona]:
    return db.query(Persona).offset(skip).limit(limit).all()


def update_persona(db: Session, persona_id: int, data: PersonaUpdate) -> Persona | None:
    db_obj = get_persona_by_id(db, persona_id)
    if not db_obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_persona(db: Session, persona_id: int) -> bool:
    db_obj = get_persona_by_id(db, persona_id)
    if not db_obj:
        return False

    db.delete(db_obj)
    db.commit()
    return True
