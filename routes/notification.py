from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.notification import Notification
from models.user import User
from schemas.notification import NotificationCreate, NotificationUpdate, NotificationResponse
from services.notification import (
    create_notification,
    get_notification_by_id,
    get_notifications,
    update_notification,
    delete_notification,
)
from routes.dependencies import normalize_role_name, require_roles
from security.tenant import ensure_user_access

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


def is_admin(user: User) -> bool:
    return normalize_role_name(user.role.name if user.role else None) == "admin"


@router.post("/", response_model=NotificationResponse)
def create_notification_endpoint(
    data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "employee", "client")),
):
    if not is_admin(current_user):
        data.user_id = current_user.id
    ensure_user_access(db, data.user_id, current_user)
    return create_notification(db, data)


@router.get("/", response_model=list[NotificationResponse])
def list_notifications_endpoint(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "employee", "client")),
):
    offset = (page - 1) * page_size
    return (
        db.query(Notification)
        .join(Notification.user)
        .filter(
            User.workspace_id == current_user.workspace_id,
            Notification.user_id == current_user.id,
        )
        .order_by(Notification.created_at.desc(), Notification.id.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification_endpoint(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "employee", "client")),
):
    db_obj = get_notification_by_id(db, notification_id)
    if not db_obj or db_obj.user.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="Notification not found")
    if db_obj.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    return db_obj


@router.put("/{notification_id}", response_model=NotificationResponse)
def update_notification_endpoint(
    notification_id: int,
    data: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "employee", "client")),
):
    db_obj = get_notification_by_id(db, notification_id)
    if not db_obj or db_obj.user.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="Notification not found")
    if db_obj.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    if not is_admin(current_user) and (
        data.user_id is not None or data.title is not None or data.content is not None
    ):
        raise HTTPException(status_code=403, detail="Only is_read can be updated")
    if is_admin(current_user) and data.user_id is not None:
        ensure_user_access(db, data.user_id, current_user)
    db_obj = update_notification(db, notification_id, data)
    return db_obj


@router.delete("/{notification_id}")
def delete_notification_endpoint(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "employee", "client")),
):
    db_obj = get_notification_by_id(db, notification_id)
    if not db_obj or db_obj.user.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="Notification not found")
    if db_obj.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    deleted = delete_notification(db, notification_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted successfully"}


@router.patch("/read-all")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "employee", "client")),
):
    updated_count = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id, Notification.is_read.is_(False))
        .update({"is_read": True}, synchronize_session=False)
    )
    db.commit()
    return {"updated": updated_count}
