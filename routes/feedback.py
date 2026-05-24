from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.feedback import Feedback
from schemas.feedback import FeedbackCreate, FeedbackUpdate, FeedbackResponse
from services.feedback import (
    create_feedback,
    get_feedback_by_id,
    get_feedbacks,
    update_feedback,
    delete_feedback,
)
from routes.dependencies import require_roles
from security.tenant import ensure_conversation_access, ensure_user_access, ensure_workspace_access

router = APIRouter(
    prefix="/feedbacks",
    tags=["Feedbacks"],
)


@router.post("/", response_model=FeedbackResponse)
def create_feedback_endpoint(
    data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    ensure_workspace_access(data.workspace_id, current_user)
    ensure_user_access(db, data.user_id, current_user)
    ensure_conversation_access(db, data.conversation_id, current_user)
    return create_feedback(db, data)


@router.get("/", response_model=list[FeedbackResponse])
def list_feedbacks_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return db.query(Feedback).filter(Feedback.workspace_id == current_user.workspace_id).offset(skip).limit(limit).all()


@router.get("/{feedback_id}", response_model=FeedbackResponse)
def get_feedback_endpoint(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_feedback_by_id(db, feedback_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return db_obj


@router.put("/{feedback_id}", response_model=FeedbackResponse)
def update_feedback_endpoint(
    feedback_id: int,
    data: FeedbackUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = get_feedback_by_id(db, feedback_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="Feedback not found")
    if data.workspace_id is not None:
        ensure_workspace_access(data.workspace_id, current_user)
    if data.user_id is not None:
        ensure_user_access(db, data.user_id, current_user)
    if data.conversation_id is not None:
        ensure_conversation_access(db, data.conversation_id, current_user)
    db_obj = update_feedback(db, feedback_id, data)
    return db_obj


@router.delete("/{feedback_id}")
def delete_feedback_endpoint(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = get_feedback_by_id(db, feedback_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="Feedback not found")
    deleted = delete_feedback(db, feedback_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return {"message": "Feedback deleted successfully"}
