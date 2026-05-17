from sqlalchemy.orm import Session
from models.persona import Persona
from schemas.persona import PersonaCreate, PersonaUpdate


def create_persona(db: Session, data: PersonaCreate):
    persona = Persona(**data.dict(exclude_unset=True))
    db.add(persona)
    db.commit()
    db.refresh(persona)
    return persona


def get_personas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Persona).offset(skip).limit(limit).all()


def get_persona_by_id(db: Session, persona_id: int):
    return db.query(Persona).filter(Persona.id == persona_id).first()


def get_personas_by_user_id(db: Session, user_id: int):
    return db.query(Persona).filter(Persona.user_id == user_id).all()


def get_personas_by_workspace_id(db: Session, workspace_id: int):
    return db.query(Persona).filter(Persona.workspace_id == workspace_id).all()


def update_persona(db: Session, persona_id: int, data: PersonaUpdate):
    persona = get_persona_by_id(db, persona_id)

    if not persona:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(persona, field, value)

    db.commit()
    db.refresh(persona)
    return persona


def delete_persona(db: Session, persona_id: int):
    persona = get_persona_by_id(db, persona_id)

    if not persona:
        return None

    db.delete(persona)
    db.commit()
    return persona