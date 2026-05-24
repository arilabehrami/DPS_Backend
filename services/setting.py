from sqlalchemy.orm import Session
from models.setting import Setting
from schemas.setting import SettingCreate, SettingUpdate


def create_setting(db: Session, data: SettingCreate) -> Setting:
    db_obj = Setting(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_setting_by_id(db: Session, setting_id: int) -> Setting | None:
    return db.query(Setting).filter(Setting.id == setting_id).first()


def get_settings(db: Session, skip: int = 0, limit: int = 100) -> list[Setting]:
    return db.query(Setting).offset(skip).limit(limit).all()


def update_setting(db: Session, setting_id: int, data: SettingUpdate) -> Setting | None:
    db_obj = get_setting_by_id(db, setting_id)
    if not db_obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_setting(db: Session, setting_id: int) -> bool:
    db_obj = get_setting_by_id(db, setting_id)
    if not db_obj:
        return False

    db.delete(db_obj)
    db.commit()
    return True
