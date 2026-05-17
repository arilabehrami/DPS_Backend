from sqlalchemy.orm import Session
from models.settings import Settings
from schemas.settings import SettingsCreate, SettingsUpdate


def create_settings(db: Session, data: SettingsCreate):
    settings = Settings(**data.dict(exclude_unset=True))
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


def get_all_settings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Settings).offset(skip).limit(limit).all()


def get_settings_by_id(db: Session, settings_id: int):
    return db.query(Settings).filter(Settings.id == settings_id).first()


def get_settings_by_user_id(db: Session, user_id: int):
    return db.query(Settings).filter(Settings.user_id == user_id).first()


def update_settings(db: Session, settings_id: int, data: SettingsUpdate):
    settings = get_settings_by_id(db, settings_id)

    if not settings:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(settings, field, value)

    db.commit()
    db.refresh(settings)
    return settings


def delete_settings(db: Session, settings_id: int):
    settings = get_settings_by_id(db, settings_id)

    if not settings:
        return None

    db.delete(settings)
    db.commit()
    return settings
    