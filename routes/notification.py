from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas.notification import NotificationCreate, NotificationUpdate, NotificationResponse
from services.notification import (
    create_notification,
    get_notification_by_id,
    get_notifications,
    update_notification,
    delete_notification,
)
from routes.dependencies import require_roles

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.post("/", response_model=NotificationResponse)
def create_notification_endpoint(
    data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    return create_notification(db, data)


@router.get("/", response_model=list[NotificationResponse])
def list_notifications_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return get_notifications(db, skip=skip, limit=limit)


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification_endpoint(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_notification_by_id(db, notification_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Notification not found")
    return db_obj


@router.put("/{notification_id}", response_model=NotificationResponse)
def update_notification_endpoint(
    notification_id: int,
    data: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = update_notification(db, notification_id, data)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Notification not found")
    return db_obj


@router.delete("/{notification_id}")
def delete_notification_endpoint(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    deleted = delete_notification(db, notification_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted successfully"}
