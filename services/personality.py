from sqlalchemy.orm import Session
from models.personality import Personality
from schemas.personality import PersonalityCreate, PersonalityUpdate


def create_personality(db: Session, data: PersonalityCreate):
    personality = Personality(**data.dict(exclude_unset=True))
    db.add(personality)
    db.commit()
    db.refresh(personality)
    return personality


def get_personalities(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Personality).offset(skip).limit(limit).all()


def get_personality_by_id(db: Session, personality_id: int):
    return db.query(Personality).filter(Personality.id == personality_id).first()


def get_personalities_by_user_id(db: Session, user_id: int):
    return db.query(Personality).filter(Personality.user_id == user_id).all()


def get_personalities_by_workspace_id(db: Session, workspace_id: int):
    return db.query(Personality).filter(Personality.workspace_id == workspace_id).all()


def search_personalities(db: Session, keyword: str):
    return db.query(Personality).filter(Personality.name.ilike(f"%{keyword}%")).all()


def update_personality(db: Session, personality_id: int, data: PersonalityUpdate):
    personality = get_personality_by_id(db, personality_id)

    if not personality:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(personality, field, value)

    db.commit()
    db.refresh(personality)
    return personality


def delete_personality(db: Session, personality_id: int):
    personality = get_personality_by_id(db, personality_id)

    if not personality:
        return None

    db.delete(personality)
    db.commit()
    return personality