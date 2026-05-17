from sqlalchemy.orm import Session
from models.feedback import Feedback
from schemas.feedback import FeedbackCreate, FeedbackUpdate


def create_feedback(db: Session, data: FeedbackCreate):
    feedback = Feedback(**data.dict(exclude_unset=True))
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def get_feedbacks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Feedback).offset(skip).limit(limit).all()


def get_feedback_by_id(db: Session, feedback_id: int):
    return db.query(Feedback).filter(Feedback.id == feedback_id).first()


def get_feedback_by_user_id(db: Session, user_id: int):
    return db.query(Feedback).filter(Feedback.user_id == user_id).all()


def update_feedback(db: Session, feedback_id: int, data: FeedbackUpdate):
    feedback = get_feedback_by_id(db, feedback_id)

    if not feedback:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(feedback, field, value)

    db.commit()
    db.refresh(feedback)
    return feedback


def delete_feedback(db: Session, feedback_id: int):
    feedback = get_feedback_by_id(db, feedback_id)

    if not feedback:
        return None

    db.delete(feedback)
    db.commit()
    return feedback