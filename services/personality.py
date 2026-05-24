from sqlalchemy.orm import Session
from models.personality import Personality
from schemas.personality import PersonalityCreate, PersonalityUpdate


def create_personality(db: Session, data: PersonalityCreate) -> Personality:
    db_obj = Personality(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_personality_by_id(db: Session, personality_id: int) -> Personality | None:
    return db.query(Personality).filter(Personality.id == personality_id).first()


def get_personalitys(db: Session, skip: int = 0, limit: int = 100) -> list[Personality]:
    return db.query(Personality).offset(skip).limit(limit).all()


def update_personality(db: Session, personality_id: int, data: PersonalityUpdate) -> Personality | None:
    db_obj = get_personality_by_id(db, personality_id)
    if not db_obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_personality(db: Session, personality_id: int) -> bool:
    db_obj = get_personality_by_id(db, personality_id)
    if not db_obj:
        return False

    db.delete(db_obj)
    db.commit()
    return True
