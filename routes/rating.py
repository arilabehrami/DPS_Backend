from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas.rating import RatingCreate, RatingUpdate, RatingResponse
from services.rating import (
    create_rating,
    get_rating_by_id,
    get_ratings,
    update_rating,
    delete_rating,
)
from routes.dependencies import require_roles

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
    return create_rating(db, data)


@router.get("/", response_model=list[RatingResponse])
def list_ratings_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return get_ratings(db, skip=skip, limit=limit)


@router.get("/{rating_id}", response_model=RatingResponse)
def get_rating_endpoint(
    rating_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_rating_by_id(db, rating_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Rating not found")
    return db_obj


@router.put("/{rating_id}", response_model=RatingResponse)
def update_rating_endpoint(
    rating_id: int,
    data: RatingUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = update_rating(db, rating_id, data)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Rating not found")
    return db_obj


@router.delete("/{rating_id}")
def delete_rating_endpoint(
    rating_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    deleted = delete_rating(db, rating_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Rating not found")
    return {"message": "Rating deleted successfully"}
