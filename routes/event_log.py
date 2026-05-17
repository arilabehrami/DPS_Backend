from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.event_log import EventLogCreate, EventLogUpdate, EventLogResponse
from services.event_log import (
    create_event_log,
    get_event_logs,
    get_event_log_by_id,
    get_event_logs_by_event_type,
    update_event_log,
    delete_event_log
)

router = APIRouter(prefix="/event-logs", tags=["Event Logs"])


@router.post("/", response_model=EventLogResponse)
def create_event_log_endpoint(data: EventLogCreate, db: Session = Depends(get_db)):
    return create_event_log(db, data)


@router.get("/", response_model=list[EventLogResponse])
def get_event_logs_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_event_logs(db, skip, limit)


@router.get("/{event_log_id}", response_model=EventLogResponse)
def get_event_log_endpoint(event_log_id: int, db: Session = Depends(get_db)):
    event_log = get_event_log_by_id(db, event_log_id)

    if not event_log:
        raise HTTPException(status_code=404, detail="Event log not found")

    return event_log


@router.get("/type/{event_type}", response_model=list[EventLogResponse])
def get_event_logs_by_type_endpoint(event_type: str, db: Session = Depends(get_db)):
    return get_event_logs_by_event_type(db, event_type)


@router.put("/{event_log_id}", response_model=EventLogResponse)
def update_event_log_endpoint(event_log_id: int, data: EventLogUpdate, db: Session = Depends(get_db)):
    event_log = update_event_log(db, event_log_id, data)

    if not event_log:
        raise HTTPException(status_code=404, detail="Event log not found")

    return event_log


@router.delete("/{event_log_id}")
def delete_event_log_endpoint(event_log_id: int, db: Session = Depends(get_db)):
    event_log = delete_event_log(db, event_log_id)

    if not event_log:
        raise HTTPException(status_code=404, detail="Event log not found")

    return {"message": "Event log deleted successfully"}