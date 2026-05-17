from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
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

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse)
def create_user_endpoint(data: UserCreate, db: Session = Depends(get_db)):
    existing_email = get_user_by_email(db, data.email)

    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    existing_username = get_user_by_username(db, data.username)

    if existing_username:
        raise HTTPException(status_code=400, detail="Username already exists")

    return create_user(db, data)


@router.get("/", response_model=list[UserResponse])
def get_users_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_users(db, skip, limit)


@router.get("/{user_id}", response_model=UserResponse)
def get_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("/email/{email}", response_model=UserResponse)
def get_user_by_email_endpoint(email: str, db: Session = Depends(get_db)):
    user = get_user_by_email(db, email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("/username/{username}", response_model=UserResponse)
def get_user_by_username_endpoint(username: str, db: Session = Depends(get_db)):
    user = get_user_by_username(db, username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("/workspace/{workspace_id}", response_model=list[UserResponse])
def get_users_by_workspace_endpoint(workspace_id: int, db: Session = Depends(get_db)):
    return get_users_by_workspace_id(db, workspace_id)


@router.get("/role/{role_id}", response_model=list[UserResponse])
def get_users_by_role_endpoint(role_id: int, db: Session = Depends(get_db)):
    return get_users_by_role_id(db, role_id)


@router.put("/{user_id}", response_model=UserResponse)
def update_user_endpoint(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    user = update_user(db, user_id, data)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.delete("/{user_id}")
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    user = delete_user(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User deleted successfully"}