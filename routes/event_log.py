from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.event_log import EventLog
from schemas.event_log import EventLogCreate, EventLogUpdate, EventLogResponse
from services.event_log import (
    create_event_log,
    get_event_log_by_id,
    get_event_logs,
    update_event_log,
    delete_event_log,
)
from routes.dependencies import require_roles
from security.tenant import ensure_user_access, ensure_workspace_access

router = APIRouter(
    prefix="/event-logs",
    tags=["Event Logs"],
)


@router.post("/", response_model=EventLogResponse)
def create_event_log_endpoint(
    data: EventLogCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    if data.workspace_id is not None:
        ensure_workspace_access(data.workspace_id, current_user)
    ensure_user_access(db, data.user_id, current_user)
    return create_event_log(db, data)


@router.get("/", response_model=list[EventLogResponse])
def list_event_logs_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return db.query(EventLog).filter(EventLog.workspace_id == current_user.workspace_id).offset(skip).limit(limit).all()


@router.get("/{event_log_id}", response_model=EventLogResponse)
def get_event_log_endpoint(
    event_log_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_event_log_by_id(db, event_log_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="EventLog not found")
    return db_obj


@router.put("/{event_log_id}", response_model=EventLogResponse)
def update_event_log_endpoint(
    event_log_id: int,
    data: EventLogUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = get_event_log_by_id(db, event_log_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="EventLog not found")
    if data.workspace_id is not None:
        ensure_workspace_access(data.workspace_id, current_user)
    if data.user_id is not None:
        ensure_user_access(db, data.user_id, current_user)
    db_obj = update_event_log(db, event_log_id, data)
    return db_obj


@router.delete("/{event_log_id}")
def delete_event_log_endpoint(
    event_log_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = get_event_log_by_id(db, event_log_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="EventLog not found")
    deleted = delete_event_log(db, event_log_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="EventLog not found")
    return {"message": "EventLog deleted successfully"}
