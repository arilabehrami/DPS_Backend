from database import SessionLocal
from models.event_log import EventLog


def record_event_log(user_id: int | None, workspace_id: int | None, event_type: str, description: str) -> None:
    db = SessionLocal()
    try:
        db.add(
            EventLog(
                user_id=user_id,
                workspace_id=workspace_id,
                event_type=event_type,
                description=description,
            )
        )
        db.commit()
    finally:
        db.close()
