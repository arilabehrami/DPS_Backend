from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.role import Role
from models.user import User
from models.workspace import Workspace
from schemas.auth import AuthResponse, AuthUserResponse, LoginRequest, RegisterRequest
from security.auth_security import (
    create_access_token,
    get_current_user,
    hash_password,
    require_roles,
    verify_password,
)


router = APIRouter(prefix="/auth", tags=["Auth"])


def build_auth_response(user: User) -> AuthResponse:
    access_token = create_access_token(
        {
            "sub": user.email,
            "user_id": user.id,
            "role": user.role.name if user.role else None,
            "workspace_id": user.workspace_id,
        }
    )

    return AuthResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "workspace_id": user.workspace_id,
            "role_id": user.role_id,
            "username": user.username,
            "email": user.email,
            "role": user.role.name if user.role else None,
        },
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing_email = db.query(User).filter(User.email == data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    existing_username = db.query(User).filter(User.username == data.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already exists")

    workspace = db.query(Workspace).filter(Workspace.id == data.workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    role = db.query(Role).filter(Role.id == data.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    user = User(
        workspace_id=data.workspace_id,
        role_id=data.role_id,
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return build_auth_response(user)


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ose password eshte gabim",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return build_auth_response(user)


@router.get("/me", response_model=AuthUserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "workspace_id": current_user.workspace_id,
        "role_id": current_user.role_id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role.name if current_user.role else None,
    }


@router.get("/admin-check", response_model=AuthUserResponse)
def admin_check(current_user: User = Depends(require_roles("admin"))):
    return {
        "id": current_user.id,
        "workspace_id": current_user.workspace_id,
        "role_id": current_user.role_id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role.name if current_user.role else None,
    }
