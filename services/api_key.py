from sqlalchemy.orm import Session
from models.api_key import ApiKey
from schemas.api_key import ApiKeyCreate, ApiKeyUpdate


def create_api_key(db: Session, data: ApiKeyCreate) -> ApiKey:
    db_obj = ApiKey(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_api_key_by_id(db: Session, api_key_id: int) -> ApiKey | None:
    return db.query(ApiKey).filter(ApiKey.id == api_key_id).first()


def get_api_keys(db: Session, skip: int = 0, limit: int = 100) -> list[ApiKey]:
    return db.query(ApiKey).offset(skip).limit(limit).all()


def update_api_key(db: Session, api_key_id: int, data: ApiKeyUpdate) -> ApiKey | None:
    db_obj = get_api_key_by_id(db, api_key_id)
    if not db_obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_api_key(db: Session, api_key_id: int) -> bool:
    db_obj = get_api_key_by_id(db, api_key_id)
    if not db_obj:
        return False

    db.delete(db_obj)
    db.commit()
    return True
