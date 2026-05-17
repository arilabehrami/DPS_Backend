from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models.feedback import Feedback

router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_feedbacks(db: Session = Depends(get_db)):
    return db.query(Feedback).all()


@router.get("/{feedback_id}")
def get_feedback(feedback_id: int, db: Session = Depends(get_db)):
    return db.query(Feedback).filter(
        Feedback.id == feedback_id
    ).first()