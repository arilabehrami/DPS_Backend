from sqlalchemy.orm import Session
from models.feedback import Feedback
from schemas.feedback import FeedbackCreate, FeedbackUpdate


def create_feedback(db: Session, data: FeedbackCreate) -> Feedback:
    db_obj = Feedback(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_feedback_by_id(db: Session, feedback_id: int) -> Feedback | None:
    return db.query(Feedback).filter(Feedback.id == feedback_id).first()


def get_feedbacks(db: Session, skip: int = 0, limit: int = 100) -> list[Feedback]:
    return db.query(Feedback).offset(skip).limit(limit).all()


def update_feedback(db: Session, feedback_id: int, data: FeedbackUpdate) -> Feedback | None:
    db_obj = get_feedback_by_id(db, feedback_id)
    if not db_obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_feedback(db: Session, feedback_id: int) -> bool:
    db_obj = get_feedback_by_id(db, feedback_id)
    if not db_obj:
        return False

    db.delete(db_obj)
    db.commit()
    return True
