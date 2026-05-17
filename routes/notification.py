from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models.notification import Notification

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_notifications(db: Session = Depends(get_db)):
    return db.query(Notification).all()


@router.get("/{notification_id}")
def get_notification(notification_id: int, db: Session = Depends(get_db)):
    return db.query(Notification).filter(
        Notification.id == notification_id
    ).first()