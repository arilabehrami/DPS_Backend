from sqlalchemy.orm import Session
from models.persona_trait import PersonaTrait
from schemas.persona_trait import PersonaTraitCreate, PersonaTraitUpdate


def create_persona_trait(db: Session, data: PersonaTraitCreate):
    persona_trait = PersonaTrait(**data.dict(exclude_unset=True))
    db.add(persona_trait)
    db.commit()
    db.refresh(persona_trait)
    return persona_trait


def get_persona_traits(db: Session, skip: int = 0, limit: int = 100):
    return db.query(PersonaTrait).offset(skip).limit(limit).all()


def get_persona_trait_by_id(db: Session, trait_id: int):
    return db.query(PersonaTrait).filter(PersonaTrait.id == trait_id).first()


def get_persona_traits_by_persona_id(db: Session, persona_id: int):
    return db.query(PersonaTrait).filter(PersonaTrait.persona_id == persona_id).all()


def update_persona_trait(db: Session, trait_id: int, data: PersonaTraitUpdate):
    persona_trait = get_persona_trait_by_id(db, trait_id)

    if not persona_trait:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(persona_trait, field, value)

    db.commit()
    db.refresh(persona_trait)
    return persona_trait


def delete_persona_trait(db: Session, trait_id: int):
    persona_trait = get_persona_trait_by_id(db, trait_id)

    if not persona_trait:
        return None

    db.delete(persona_trait)
    db.commit()
    return persona_trait