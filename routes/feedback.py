from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.feedback import FeedbackCreate, FeedbackUpdate, FeedbackResponse
from services.feedback import (
    create_feedback,
    get_feedbacks,
    get_feedback_by_id,
    get_feedback_by_user_id,
    update_feedback,
    delete_feedback
)

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("/", response_model=FeedbackResponse)
def create_feedback_endpoint(data: FeedbackCreate, db: Session = Depends(get_db)):
    return create_feedback(db, data)


@router.get("/", response_model=list[FeedbackResponse])
def get_feedbacks_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_feedbacks(db, skip, limit)


@router.get("/{feedback_id}", response_model=FeedbackResponse)
def get_feedback_endpoint(feedback_id: int, db: Session = Depends(get_db)):
    feedback = get_feedback_by_id(db, feedback_id)

    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    return feedback


@router.get("/user/{user_id}", response_model=list[FeedbackResponse])
def get_feedback_by_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    return get_feedback_by_user_id(db, user_id)


@router.put("/{feedback_id}", response_model=FeedbackResponse)
def update_feedback_endpoint(feedback_id: int, data: FeedbackUpdate, db: Session = Depends(get_db)):
    feedback = update_feedback(db, feedback_id, data)

    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    return feedback


@router.delete("/{feedback_id}")
def delete_feedback_endpoint(feedback_id: int, db: Session = Depends(get_db)):
    feedback = delete_feedback(db, feedback_id)

    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    return {"message": "Feedback deleted successfully"}