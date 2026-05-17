from sqlalchemy.orm import Session
from models.event_log import EventLog
from schemas.event_log import EventLogCreate, EventLogUpdate


def create_event_log(db: Session, data: EventLogCreate):
    event_log = EventLog(**data.dict(exclude_unset=True))
    db.add(event_log)
    db.commit()
    db.refresh(event_log)
    return event_log


def get_event_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(EventLog).offset(skip).limit(limit).all()


def get_event_log_by_id(db: Session, event_log_id: int):
    return db.query(EventLog).filter(EventLog.id == event_log_id).first()


def get_event_logs_by_event_type(db: Session, event_type: str):
    return db.query(EventLog).filter(EventLog.event_type == event_type).all()


def update_event_log(db: Session, event_log_id: int, data: EventLogUpdate):
    event_log = get_event_log_by_id(db, event_log_id)

    if not event_log:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(event_log, field, value)

    db.commit()
    db.refresh(event_log)
    return event_log


def delete_event_log(db: Session, event_log_id: int):
    event_log = get_event_log_by_id(db, event_log_id)

    if not event_log:
        return None

    db.delete(event_log)
    db.commit()
    return event_log