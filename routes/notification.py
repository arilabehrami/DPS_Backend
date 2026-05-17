from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.notification import NotificationCreate, NotificationUpdate, NotificationResponse
from services.notification import (
    create_notification,
    get_notifications,
    get_notification_by_id,
    get_notifications_by_user_id,
    mark_notification_as_read,
    update_notification,
    delete_notification
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/", response_model=NotificationResponse)
def create_notification_endpoint(data: NotificationCreate, db: Session = Depends(get_db)):
    return create_notification(db, data)


@router.get("/", response_model=list[NotificationResponse])
def get_notifications_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_notifications(db, skip, limit)


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification_endpoint(notification_id: int, db: Session = Depends(get_db)):
    notification = get_notification_by_id(db, notification_id)

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return notification


@router.get("/user/{user_id}", response_model=list[NotificationResponse])
def get_notifications_by_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    return get_notifications_by_user_id(db, user_id)


@router.put("/{notification_id}", response_model=NotificationResponse)
def update_notification_endpoint(notification_id: int, data: NotificationUpdate, db: Session = Depends(get_db)):
    notification = update_notification(db, notification_id, data)

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return notification


@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read_endpoint(notification_id: int, db: Session = Depends(get_db)):
    notification = mark_notification_as_read(db, notification_id)

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return notification


@router.delete("/{notification_id}")
def delete_notification_endpoint(notification_id: int, db: Session = Depends(get_db)):
    notification = delete_notification(db, notification_id)

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return {"message": "Notification deleted successfully"}