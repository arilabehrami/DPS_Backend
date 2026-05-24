from sqlalchemy.orm import Session
from models.persona_trait import PersonaTrait
from schemas.persona_trait import PersonaTraitCreate, PersonaTraitUpdate


def create_persona_trait(db: Session, data: PersonaTraitCreate) -> PersonaTrait:
    db_obj = PersonaTrait(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_persona_trait_by_id(db: Session, persona_trait_id: int) -> PersonaTrait | None:
    return db.query(PersonaTrait).filter(PersonaTrait.id == persona_trait_id).first()


def get_persona_traits(db: Session, skip: int = 0, limit: int = 100) -> list[PersonaTrait]:
    return db.query(PersonaTrait).offset(skip).limit(limit).all()


def update_persona_trait(db: Session, persona_trait_id: int, data: PersonaTraitUpdate) -> PersonaTrait | None:
    db_obj = get_persona_trait_by_id(db, persona_trait_id)
    if not db_obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_persona_trait(db: Session, persona_trait_id: int) -> bool:
    db_obj = get_persona_trait_by_id(db, persona_trait_id)
    if not db_obj:
        return False

    db.delete(db_obj)
    db.commit()
    return True
