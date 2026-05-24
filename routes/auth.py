from datetime import datetime, timedelta, timezone
import os

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database import get_db
from models.role import Role
from models.user import User
from models.workspace import Workspace
from schemas.user import UserCreate
from services.user import create_user, get_user_by_email
from routes.dependencies import get_current_user, normalize_role_name, require_roles

router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@dps.com").lower()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    username: str | None = None
    full_name: str | None = None
    email: EmailStr
    password: str
    workspace_id: int | None = 1
    role_id: int | None = None


class UserFrontendResponse(BaseModel):
    id: int
    name: str
    full_name: str
    username: str | None = None
    email: EmailStr
    workspace_id: int
    role_id: int
    role: str

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    access_token: str
    token: str
    token_type: str = "bearer"
    user: UserFrontendResponse


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user: User) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user.id), "email": user.email, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def frontend_user(user: User) -> UserFrontendResponse:
    return UserFrontendResponse(
        id=user.id,
        full_name=user.full_name,
        username=user.username,
        email=user.email,
        workspace_id=user.workspace_id,
        role_id=user.role_id,
        name=user.full_name,
        role=normalize_role_name(user.role.name if user.role else None),
    )


def get_or_create_role(db: Session, name: str) -> Role:
    role = db.query(Role).filter(Role.name == name).first()
    if role:
        return role

    role = Role(name=name)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def enforce_single_admin_account(db: Session, user: User) -> User:
    admin_role = get_or_create_role(db, "admin")
    employee_role = get_or_create_role(db, "employee")

    if user.email.lower() == ADMIN_EMAIL:
        if user.role_id != admin_role.id:
            user.role_id = admin_role.id
            db.commit()
            db.refresh(user)
        return user

    if user.role and user.role.name.lower() == "admin":
        user.role_id = employee_role.id
        db.commit()
        db.refresh(user)

    return user


def ensure_default_workspace_and_employee_role(db: Session, workspace_id: int | None) -> tuple[int, int]:
    workspace = db.query(Workspace).filter(Workspace.id == (workspace_id or 1)).first()
    if not workspace:
        workspace = Workspace(name="Default Workspace")
        db.add(workspace)
        db.commit()
        db.refresh(workspace)

    role = get_or_create_role(db, "employee")

    return workspace.id, role.id


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    workspace_id, role_id = ensure_default_workspace_and_employee_role(db, data.workspace_id)
    username = data.username or data.email.split("@")[0]
    full_name = data.full_name or username

    user_create = UserCreate(
        full_name=full_name,
        username=username,
        email=data.email,
        password=data.password,
        workspace_id=workspace_id,
        role_id=role_id,
    )
    user = create_user(db, user_create)
    user = enforce_single_admin_account(db, user)
    token = create_access_token(user)
    return AuthResponse(access_token=token, token=token, user=frontend_user(user))


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user = enforce_single_admin_account(db, user)
    token = create_access_token(user)
    return AuthResponse(access_token=token, token=token, user=frontend_user(user))


@router.get("/me", response_model=UserFrontendResponse)
def me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user = enforce_single_admin_account(db, current_user)
    return frontend_user(current_user)


@router.get("/admin-check")
def admin_check(current_user: User = Depends(require_roles("admin"))):
    return {"message": "Admin access granted", "user_id": current_user.id}
