from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.rating import Rating
from schemas.rating import RatingCreate, RatingUpdate, RatingResponse
from services.rating import (
    create_rating,
    get_rating_by_id,
    get_ratings,
    update_rating,
    delete_rating,
)
from routes.dependencies import require_roles
from security.tenant import ensure_conversation_access, ensure_personality_access, ensure_user_access, ensure_workspace_access

router = APIRouter(
    prefix="/ratings",
    tags=["Ratings"],
)


@router.post("/", response_model=RatingResponse)
def create_rating_endpoint(
    data: RatingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    ensure_workspace_access(data.workspace_id, current_user)
    ensure_user_access(db, data.user_id, current_user)
    ensure_personality_access(db, data.personality_id, current_user)
    ensure_conversation_access(db, data.conversation_id, current_user)
    return create_rating(db, data)


@router.get("/", response_model=list[RatingResponse])
def list_ratings_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return db.query(Rating).filter(Rating.workspace_id == current_user.workspace_id).offset(skip).limit(limit).all()


@router.get("/{rating_id}", response_model=RatingResponse)
def get_rating_endpoint(
    rating_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_rating_by_id(db, rating_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="Rating not found")
    return db_obj


@router.put("/{rating_id}", response_model=RatingResponse)
def update_rating_endpoint(
    rating_id: int,
    data: RatingUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = get_rating_by_id(db, rating_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="Rating not found")
    if data.workspace_id is not None:
        ensure_workspace_access(data.workspace_id, current_user)
    if data.user_id is not None:
        ensure_user_access(db, data.user_id, current_user)
    if data.personality_id is not None:
        ensure_personality_access(db, data.personality_id, current_user)
    if data.conversation_id is not None:
        ensure_conversation_access(db, data.conversation_id, current_user)
    db_obj = update_rating(db, rating_id, data)
    return db_obj


@router.delete("/{rating_id}")
def delete_rating_endpoint(
    rating_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = get_rating_by_id(db, rating_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="Rating not found")
    deleted = delete_rating(db, rating_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Rating not found")
    return {"message": "Rating deleted successfully"}
