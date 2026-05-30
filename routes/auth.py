from datetime import datetime, timedelta, timezone
import os
import hashlib
import secrets
from urllib.parse import parse_qs

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models.password_change_otp import PasswordChangeOTP
from models.password_reset_otp import PasswordResetOTP
from models.registration_otp import RegistrationOTP
from models.role import Role
from models.user import User
from models.workspace import Workspace
from schemas.user import UserCreate
from services.user import get_user_by_email
from routes.dependencies import get_current_user, normalize_role_name, require_roles
from services.background_jobs import send_email_job
from services.email_service import send_email

router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@dps.com").lower()
REGISTER_CLIENT_ROLE_ID = 3
PUBLIC_REGISTER_WORKSPACE_ID = int(os.getenv("PUBLIC_REGISTER_WORKSPACE_ID", "1"))
OTP_EXPIRE_MINUTES = int(os.getenv("REGISTER_OTP_EXPIRE_MINUTES", "10"))
OTP_RESEND_SECONDS = int(os.getenv("REGISTER_OTP_RESEND_SECONDS", "60"))
OTP_MAX_ATTEMPTS = int(os.getenv("REGISTER_OTP_MAX_ATTEMPTS", "5"))
OTP_SECRET = os.getenv("REGISTER_OTP_SECRET", SECRET_KEY)
RESET_OTP_EXPIRE_MINUTES = int(os.getenv("RESET_OTP_EXPIRE_MINUTES", "10"))
RESET_OTP_RESEND_SECONDS = int(os.getenv("RESET_OTP_RESEND_SECONDS", "60"))
RESET_OTP_MAX_ATTEMPTS = int(os.getenv("RESET_OTP_MAX_ATTEMPTS", "5"))
RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", "10"))
CHANGE_OTP_EXPIRE_MINUTES = int(os.getenv("CHANGE_OTP_EXPIRE_MINUTES", "10"))
CHANGE_OTP_RESEND_SECONDS = int(os.getenv("CHANGE_OTP_RESEND_SECONDS", "60"))
CHANGE_OTP_MAX_ATTEMPTS = int(os.getenv("CHANGE_OTP_MAX_ATTEMPTS", "5"))

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


class RegisterOTPVerifyRequest(BaseModel):
    email: EmailStr
    code: str


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


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordVerifyRequest(BaseModel):
    email: EmailStr
    code: str


class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str


class ResetPasswordVerifyResponse(BaseModel):
    reset_token: str
    token_type: str = "reset"


class ChangePasswordRequestOTPResponse(BaseModel):
    detail: str


class ChangePasswordConfirmRequest(BaseModel):
    code: str
    current_password: str
    new_password: str


ROLE_LABEL_BY_ID = {
    1: "employee",
    2: "admin",
    3: "client",
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user: User) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user.id), "email": user.email, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def frontend_user(user: User) -> UserFrontendResponse:
    role_label = ROLE_LABEL_BY_ID.get(
        user.role_id,
        normalize_role_name(user.role.name if user.role else None),
    )
    return UserFrontendResponse(
        id=user.id,
        full_name=user.full_name,
        username=user.username,
        email=user.email,
        workspace_id=user.workspace_id,
        role_id=user.role_id,
        name=user.full_name,
        role=role_label,
    )


def hash_otp(email: str, code: str) -> str:
    raw = f"{email.lower().strip()}:{code.strip()}:{OTP_SECRET}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def generate_otp_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def create_reset_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": email.lower().strip(), "purpose": "password_reset", "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


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
    # Multiple admin users are allowed.
    return user


def ensure_default_workspace_and_client_role(db: Session) -> tuple[int, int]:
    workspace = db.query(Workspace).filter(Workspace.id == PUBLIC_REGISTER_WORKSPACE_ID).first()
    if not workspace:
        workspace = Workspace(name="Default Workspace")
        db.add(workspace)
        db.commit()
        db.refresh(workspace)

    role = db.query(Role).filter(Role.name == "client").first()
    if role is None:
        role = db.query(Role).filter(Role.id == REGISTER_CLIENT_ROLE_ID).first()
    if role is None:
        role = get_or_create_role(db, "client")

    return workspace.id, role.id


@router.post("/register/request-otp")
def register_request_otp(
    data: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    existing_user = get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    now = datetime.now(timezone.utc)
    pending = db.query(RegistrationOTP).filter(RegistrationOTP.email == data.email).first()
    if pending and pending.last_sent_at and (now - pending.last_sent_at).total_seconds() < OTP_RESEND_SECONDS:
        raise HTTPException(
            status_code=429,
            detail=f"Please wait {OTP_RESEND_SECONDS} seconds before requesting a new code",
        )

    workspace_id, role_id = ensure_default_workspace_and_client_role(db)
    username = data.username or data.email.split("@")[0]
    full_name = data.full_name or username
    password_hash = pwd_context.hash(data.password)
    code = generate_otp_code()
    code_hash = hash_otp(data.email, code)
    expires_at = now + timedelta(minutes=OTP_EXPIRE_MINUTES)

    if pending:
        pending.username = username
        pending.full_name = full_name
        pending.password_hash = password_hash
        pending.workspace_id = workspace_id
        pending.role_id = role_id
        pending.otp_hash = code_hash
        pending.attempts = 0
        pending.expires_at = expires_at
        pending.last_sent_at = now
    else:
        pending = RegistrationOTP(
            email=data.email,
            username=username,
            full_name=full_name,
            password_hash=password_hash,
            workspace_id=workspace_id,
            role_id=role_id,
            otp_hash=code_hash,
            attempts=0,
            expires_at=expires_at,
            last_sent_at=now,
        )
        db.add(pending)
    db.commit()

    background_tasks.add_task(
        send_email_job,
        data.email,
        "Your DPS verification code",
        f"Your verification code is: {code}. It expires in {OTP_EXPIRE_MINUTES} minutes.",
        None,
        workspace_id,
    )
    return {"detail": "Verification code sent to your email"}


@router.post("/register")
def register_alias_request_otp(
    data: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    return register_request_otp(data, background_tasks, db)


@router.post("/request-otp")
def request_otp_alias(
    data: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    return register_request_otp(data, background_tasks, db)


@router.post("/register/verify-otp", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register_verify_otp(
    data: RegisterOTPVerifyRequest,
    db: Session = Depends(get_db),
):
    existing_user = get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    pending = db.query(RegistrationOTP).filter(RegistrationOTP.email == data.email).first()
    if not pending:
        raise HTTPException(status_code=404, detail="No pending registration for this email")

    now = datetime.now(timezone.utc)
    expires_at = pending.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < now:
        db.delete(pending)
        db.commit()
        raise HTTPException(status_code=400, detail="Verification code expired")

    if pending.attempts >= OTP_MAX_ATTEMPTS:
        db.delete(pending)
        db.commit()
        raise HTTPException(status_code=429, detail="Too many invalid attempts. Request a new code.")

    provided_hash = hash_otp(data.email, data.code)
    if provided_hash != pending.otp_hash:
        pending.attempts += 1
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid verification code")

    user_create = UserCreate(
        full_name=pending.full_name or (pending.username or data.email.split("@")[0]),
        username=pending.username or data.email.split("@")[0],
        email=data.email,
        password=pending.password_hash,
        workspace_id=pending.workspace_id or 1,
        role_id=pending.role_id or REGISTER_CLIENT_ROLE_ID,
    )
    # password is already hashed in pending record; create_user expects plain password.
    user = User(
        full_name=user_create.full_name,
        username=user_create.username,
        email=user_create.email,
        hashed_password=pending.password_hash,
        workspace_id=user_create.workspace_id,
        role_id=user_create.role_id,
    )
    db.add(user)
    db.delete(pending)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    db.refresh(user)

    user = enforce_single_admin_account(db, user)
    token = create_access_token(user)
    return AuthResponse(access_token=token, token=token, user=frontend_user(user))


@router.post("/verify-otp", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def verify_otp_alias(
    data: RegisterOTPVerifyRequest,
    db: Session = Depends(get_db),
):
    return register_verify_otp(data, db)


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


@router.post("/token", response_model=TokenResponse)
async def login_token(
    request: Request,
    db: Session = Depends(get_db),
):
    body = (await request.body()).decode()
    form = parse_qs(body)
    username = (form.get("username", [""])[0] or "").strip()
    password = (form.get("password", [""])[0] or "").strip()

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="username and password are required",
        )

    user = get_user_by_email(db, username)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user = enforce_single_admin_account(db, user)
    token = create_access_token(user)
    return TokenResponse(access_token=token)


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


@router.post("/change-password/request-otp", response_model=ChangePasswordRequestOTPResponse)
def change_password_request_otp(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "employee", "client")),
):
    now = datetime.now(timezone.utc)
    pending = db.query(PasswordChangeOTP).filter(PasswordChangeOTP.email == current_user.email).first()
    if pending and pending.last_sent_at and (now - pending.last_sent_at).total_seconds() < CHANGE_OTP_RESEND_SECONDS:
        raise HTTPException(
            status_code=429,
            detail=f"Please wait {CHANGE_OTP_RESEND_SECONDS} seconds before requesting a new code",
        )

    code = generate_otp_code()
    code_hash = hash_otp(current_user.email, code)
    expires_at = now + timedelta(minutes=CHANGE_OTP_EXPIRE_MINUTES)

    if pending:
        pending.otp_hash = code_hash
        pending.attempts = 0
        pending.expires_at = expires_at
        pending.last_sent_at = now
    else:
        pending = PasswordChangeOTP(
            email=current_user.email,
            otp_hash=code_hash,
            attempts=0,
            expires_at=expires_at,
            last_sent_at=now,
        )
        db.add(pending)
    db.commit()

    send_email(
        to_email=current_user.email,
        subject="Your password change code",
        content=f"Your password change OTP is: {code}. It expires in {CHANGE_OTP_EXPIRE_MINUTES} minutes.",
    )
    return ChangePasswordRequestOTPResponse(detail="OTP sent to your email")


@router.post("/change-password/confirm")
def change_password_confirm(
    data: ChangePasswordConfirmRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "employee", "client")),
):
    if len(data.new_password or "") < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if data.current_password == data.new_password:
        raise HTTPException(status_code=400, detail="New password must be different from current password")
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    pending = db.query(PasswordChangeOTP).filter(PasswordChangeOTP.email == current_user.email).first()
    if not pending:
        raise HTTPException(status_code=404, detail="No pending password change request")

    now = datetime.now(timezone.utc)
    expires_at = pending.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < now:
        db.delete(pending)
        db.commit()
        raise HTTPException(status_code=400, detail="Verification code expired")

    if pending.attempts >= CHANGE_OTP_MAX_ATTEMPTS:
        db.delete(pending)
        db.commit()
        raise HTTPException(status_code=429, detail="Too many invalid attempts. Request a new code.")

    if hash_otp(current_user.email, data.code) != pending.otp_hash:
        pending.attempts += 1
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid verification code")

    db_user = db.query(User).filter(User.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.hashed_password = pwd_context.hash(data.new_password)
    db.delete(pending)
    db.commit()
    return {"detail": "Password changed successfully"}


@router.post("/forgot-password/request-otp")
def forgot_password_request_otp(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    pending = db.query(PasswordResetOTP).filter(PasswordResetOTP.email == data.email).first()
    if pending and pending.last_sent_at and (now - pending.last_sent_at).total_seconds() < RESET_OTP_RESEND_SECONDS:
        raise HTTPException(
            status_code=429,
            detail=f"Please wait {RESET_OTP_RESEND_SECONDS} seconds before requesting a new code",
        )

    user = get_user_by_email(db, data.email)
    if user:
        code = generate_otp_code()
        code_hash = hash_otp(data.email, code)
        expires_at = now + timedelta(minutes=RESET_OTP_EXPIRE_MINUTES)
        if pending:
            pending.otp_hash = code_hash
            pending.attempts = 0
            pending.expires_at = expires_at
            pending.last_sent_at = now
        else:
            pending = PasswordResetOTP(
                email=data.email,
                otp_hash=code_hash,
                attempts=0,
                expires_at=expires_at,
                last_sent_at=now,
            )
            db.add(pending)
        db.commit()
        try:
            send_email(
                to_email=data.email,
                subject="Your password reset code",
                content=f"Your reset code is: {code}. It expires in {RESET_OTP_EXPIRE_MINUTES} minutes.",
            )
        except Exception:
            pass

    # Neutral response to avoid user enumeration.
    return {"detail": "If the email exists, an OTP has been sent"}


@router.post("/forgot-password/verify-otp", response_model=ResetPasswordVerifyResponse)
def forgot_password_verify_otp(
    data: ForgotPasswordVerifyRequest,
    db: Session = Depends(get_db),
):
    pending = db.query(PasswordResetOTP).filter(PasswordResetOTP.email == data.email).first()
    if not pending:
        raise HTTPException(status_code=404, detail="No pending password reset for this email")

    now = datetime.now(timezone.utc)
    expires_at = pending.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < now:
        db.delete(pending)
        db.commit()
        raise HTTPException(status_code=400, detail="Verification code expired")

    if pending.attempts >= RESET_OTP_MAX_ATTEMPTS:
        db.delete(pending)
        db.commit()
        raise HTTPException(status_code=429, detail="Too many invalid attempts. Request a new code.")

    if hash_otp(data.email, data.code) != pending.otp_hash:
        pending.attempts += 1
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid verification code")

    reset_token = create_reset_token(data.email)
    return ResetPasswordVerifyResponse(reset_token=reset_token)


@router.post("/forgot-password/reset")
def forgot_password_reset(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    if len(data.new_password or "") < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    try:
        payload = jwt.decode(data.reset_token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired reset token")

    if payload.get("purpose") != "password_reset":
        raise HTTPException(status_code=401, detail="Invalid reset token")

    email = (payload.get("sub") or "").strip().lower()
    if not email:
        raise HTTPException(status_code=401, detail="Invalid reset token")

    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = pwd_context.hash(data.new_password)
    pending = db.query(PasswordResetOTP).filter(PasswordResetOTP.email == email).first()
    if pending:
        db.delete(pending)
    db.commit()
    return {"detail": "Password reset successful"}
