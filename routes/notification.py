from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.notification import Notification
from models.user import User
from security.auth_security import get_current_user
from security.tenant import ensure_notification_access, ensure_user_access
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

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=NotificationResponse)
def create_notification_endpoint(
    data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.user_id is not None:
        ensure_user_access(db, data.user_id, current_user)
    return create_notification(db, data)


@router.get("/", response_model=list[NotificationResponse])
def get_notifications_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Notification)
        .join(User, Notification.user_id == User.id)
        .filter(User.workspace_id == current_user.workspace_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification_endpoint(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ensure_notification_access(db, notification_id, current_user)


@router.get("/user/{user_id}", response_model=list[NotificationResponse])
def get_notifications_by_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_user_access(db, user_id, current_user)
    return get_notifications_by_user_id(db, user_id)


@router.put("/{notification_id}", response_model=NotificationResponse)
def update_notification_endpoint(
    notification_id: int,
    data: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_notification_access(db, notification_id, current_user)
    notification = update_notification(db, notification_id, data)

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return notification


@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read_endpoint(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_notification_access(db, notification_id, current_user)
    notification = mark_notification_as_read(db, notification_id)

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return notification


@router.delete("/{notification_id}")
def delete_notification_endpoint(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_notification_access(db, notification_id, current_user)
    notification = delete_notification(db, notification_id)

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return {"message": "Notification deleted successfully"}
