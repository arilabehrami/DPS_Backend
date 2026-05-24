from sqlalchemy.orm import Session
from models.notification import Notification
from schemas.notification import NotificationCreate, NotificationUpdate


def create_notification(db: Session, data: NotificationCreate) -> Notification:
    db_obj = Notification(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_notification_by_id(db: Session, notification_id: int) -> Notification | None:
    return db.query(Notification).filter(Notification.id == notification_id).first()


def get_notifications(db: Session, skip: int = 0, limit: int = 100) -> list[Notification]:
    return db.query(Notification).offset(skip).limit(limit).all()


def update_notification(db: Session, notification_id: int, data: NotificationUpdate) -> Notification | None:
    db_obj = get_notification_by_id(db, notification_id)
    if not db_obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_notification(db: Session, notification_id: int) -> bool:
    db_obj = get_notification_by_id(db, notification_id)
    if not db_obj:
        return False

    db.delete(db_obj)
    db.commit()
    return True
