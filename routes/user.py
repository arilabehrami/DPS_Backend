from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from database import get_db
from models.feedback import Feedback
from models.rating import Rating
from models.user import User
from models.role import Role
from schemas.user import UserCreate, UserUpdate, UserResponse
from services.user import (
    create_user,
    get_user_by_id,
    get_users,
    update_user,
    delete_user,
)
from routes.dependencies import normalize_role_name, require_roles
from security.tenant import ensure_workspace_access

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


def is_admin(user) -> bool:
    return normalize_role_name(user.role.name if user.role else None) == "admin"


def ensure_single_admin(db: Session, role_id: int, user_id: int | None = None) -> None:
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role or role.name.lower() != "admin":
        return

    query = db.query(User).join(Role).filter(Role.name.ilike("admin"))
    if user_id is not None:
        query = query.filter(User.id != user_id)
    if query.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only one admin user is allowed",
        )


def attach_latest_rating(db: Session, user: User) -> User:
    latest_feedback = (
        db.query(Feedback)
        .filter(Feedback.user_id == user.id, Feedback.workspace_id == user.workspace_id)
        .order_by(desc(Feedback.created_at), desc(Feedback.id))
        .first()
    )
    latest_rating_value = latest_feedback.rating if latest_feedback else None

    if latest_rating_value is None:
        latest_rating = (
            db.query(Rating)
            .filter(Rating.user_id == user.id, Rating.workspace_id == user.workspace_id)
            .order_by(desc(Rating.created_at), desc(Rating.id))
            .first()
        )
        latest_rating_value = latest_rating.score if latest_rating else None

    user.last_rate = latest_rating_value
    user.latest_rating = latest_rating_value
    user.rating = latest_rating_value
    user.lastRate = latest_rating_value
    user.latestRating = latest_rating_value
    return user


@router.post("/", response_model=UserResponse)
def create_user_endpoint(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    ensure_workspace_access(data.workspace_id, current_user)
    ensure_single_admin(db, data.role_id)
    return create_user(db, data)


@router.get("/", response_model=list[UserResponse])
def list_users_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    users = (
        db.query(User)
        .filter(User.workspace_id == current_user.workspace_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [attach_latest_rating(db, user) for user in users]


@router.get("/{user_id}", response_model=UserResponse)
def get_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_user_by_id(db, user_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="User not found")
    if not is_admin(current_user) and db_obj.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Users can only access their own profile",
        )
    return attach_latest_rating(db, db_obj)


@router.put("/{user_id}", response_model=UserResponse)
def update_user_endpoint(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = get_user_by_id(db, user_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="User not found")
    if data.workspace_id is not None:
        ensure_workspace_access(data.workspace_id, current_user)
    if data.role_id is not None:
        ensure_single_admin(db, data.role_id, user_id=user_id)
    db_obj = update_user(db, user_id, data)
    return db_obj


@router.delete("/{user_id}")
def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = get_user_by_id(db, user_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="User not found")
    deleted = delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
