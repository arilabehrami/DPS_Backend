from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from security.auth_security import require_roles
from security.tenant import ensure_workspace_access
from models.user import User
from schemas.user import UserCreate, UserUpdate, UserResponse
from services.user import (
    create_user,
    get_users,
    get_user_by_id,
    get_user_by_email,
    get_user_by_username,
    get_users_by_workspace_id,
    get_users_by_role_id,
    update_user,
    delete_user
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(require_roles("admin"))],
)


@router.post("/", response_model=UserResponse)
def create_user_endpoint(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    ensure_workspace_access(data.workspace_id, current_user)
    existing_email = get_user_by_email(db, data.email)

    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    existing_username = get_user_by_username(db, data.username)

    if existing_username:
        raise HTTPException(status_code=400, detail="Username already exists")

    return create_user(db, data)


@router.get("/", response_model=list[UserResponse])
def get_users_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return (
        db.query(User)
        .filter(User.workspace_id == current_user.workspace_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    user = get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    ensure_workspace_access(user.workspace_id, current_user)

    return user


@router.get("/email/{email}", response_model=UserResponse)
def get_user_by_email_endpoint(
    email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    user = get_user_by_email(db, email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    ensure_workspace_access(user.workspace_id, current_user)

    return user


@router.get("/username/{username}", response_model=UserResponse)
def get_user_by_username_endpoint(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    user = get_user_by_username(db, username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    ensure_workspace_access(user.workspace_id, current_user)

    return user


@router.get("/workspace/{workspace_id}", response_model=list[UserResponse])
def get_users_by_workspace_endpoint(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    ensure_workspace_access(workspace_id, current_user)
    return get_users_by_workspace_id(db, workspace_id)


@router.get("/role/{role_id}", response_model=list[UserResponse])
def get_users_by_role_endpoint(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return (
        db.query(User)
        .filter(User.role_id == role_id)
        .filter(User.workspace_id == current_user.workspace_id)
        .all()
    )


@router.put("/{user_id}", response_model=UserResponse)
def update_user_endpoint(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    ensure_workspace_access(user.workspace_id, current_user)
    if data.workspace_id is not None:
        ensure_workspace_access(data.workspace_id, current_user)

    user = update_user(db, user_id, data)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.delete("/{user_id}")
def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    ensure_workspace_access(user.workspace_id, current_user)
    user = delete_user(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User deleted successfully"}
