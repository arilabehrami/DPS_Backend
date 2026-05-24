from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas.event_log import EventLogCreate, EventLogUpdate, EventLogResponse
from services.event_log import (
    create_event_log,
    get_event_log_by_id,
    get_event_logs,
    update_event_log,
    delete_event_log,
)
from routes.dependencies import require_roles

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
    return create_event_log(db, data)


@router.get("/", response_model=list[EventLogResponse])
def list_event_logs_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return get_event_logs(db, skip=skip, limit=limit)


@router.get("/{event_log_id}", response_model=EventLogResponse)
def get_event_log_endpoint(
    event_log_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_event_log_by_id(db, event_log_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="EventLog not found")
    return db_obj


@router.put("/{event_log_id}", response_model=EventLogResponse)
def update_event_log_endpoint(
    event_log_id: int,
    data: EventLogUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = update_event_log(db, event_log_id, data)
    if not db_obj:
        raise HTTPException(status_code=404, detail="EventLog not found")
    return db_obj


@router.delete("/{event_log_id}")
def delete_event_log_endpoint(
    event_log_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    deleted = delete_event_log(db, event_log_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="EventLog not found")
    return {"message": "EventLog deleted successfully"}
