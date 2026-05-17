from sqlalchemy.orm import Session
from models.notification import Notification
from schemas.notification import NotificationCreate, NotificationUpdate


def create_notification(db: Session, data: NotificationCreate):
    notification = Notification(**data.dict(exclude_unset=True))
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_notifications(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Notification).offset(skip).limit(limit).all()


def get_notification_by_id(db: Session, notification_id: int):
    return db.query(Notification).filter(Notification.id == notification_id).first()


def get_notifications_by_user_id(db: Session, user_id: int):
    return db.query(Notification).filter(Notification.user_id == user_id).all()


def mark_notification_as_read(db: Session, notification_id: int):
    notification = get_notification_by_id(db, notification_id)

    if not notification:
        return None

    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


def update_notification(db: Session, notification_id: int, data: NotificationUpdate):
    notification = get_notification_by_id(db, notification_id)

    if not notification:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(notification, field, value)

    db.commit()
    db.refresh(notification)
    return notification


def delete_notification(db: Session, notification_id: int):
    notification = get_notification_by_id(db, notification_id)

    if not notification:
        return None

    db.delete(notification)
    db.commit()
    return notification