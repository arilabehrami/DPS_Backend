from sqlalchemy.orm import Session
from models.api_key import APIKey
from schemas.api_key import APIKeyCreate, APIKeyUpdate


def create_api_key(db: Session, data: APIKeyCreate):
    api_key = APIKey(**data.dict(exclude_unset=True))
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key


def get_api_keys(db: Session, skip: int = 0, limit: int = 100):
    return db.query(APIKey).offset(skip).limit(limit).all()


def get_api_key_by_id(db: Session, api_key_id: int):
    return db.query(APIKey).filter(APIKey.id == api_key_id).first()


def get_api_keys_by_user_id(db: Session, user_id: int):
    return db.query(APIKey).filter(APIKey.user_id == user_id).all()


def update_api_key(db: Session, api_key_id: int, data: APIKeyUpdate):
    api_key = get_api_key_by_id(db, api_key_id)

    if not api_key:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(api_key, field, value)

    db.commit()
    db.refresh(api_key)
    return api_key


def delete_api_key(db: Session, api_key_id: int):
    api_key = get_api_key_by_id(db, api_key_id)

    if not api_key:
        return None

    db.delete(api_key)
    db.commit()
    return api_key