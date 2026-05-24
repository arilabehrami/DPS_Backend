from sqlalchemy.orm import Session
from models.event_log import EventLog
from schemas.event_log import EventLogCreate, EventLogUpdate


def create_event_log(db: Session, data: EventLogCreate) -> EventLog:
    db_obj = EventLog(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_event_log_by_id(db: Session, event_log_id: int) -> EventLog | None:
    return db.query(EventLog).filter(EventLog.id == event_log_id).first()


def get_event_logs(db: Session, skip: int = 0, limit: int = 100) -> list[EventLog]:
    return db.query(EventLog).offset(skip).limit(limit).all()


def update_event_log(db: Session, event_log_id: int, data: EventLogUpdate) -> EventLog | None:
    db_obj = get_event_log_by_id(db, event_log_id)
    if not db_obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_event_log(db: Session, event_log_id: int) -> bool:
    db_obj = get_event_log_by_id(db, event_log_id)
    if not db_obj:
        return False

    db.delete(db_obj)
    db.commit()
    return True
