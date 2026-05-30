from datetime import datetime, timedelta, timezone
import hashlib
import os
import secrets

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import desc, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models.feedback import Feedback
from models.registration_otp import RegistrationOTP
from models.rating import Rating
from models.user import User
from models.role import Role
from schemas.user import AllowedRecipientResponse, UserCreate, UserUpdate, UserResponse
from services.background_jobs import send_email_job
from services.user import (
    get_user_by_id,
    update_user,
    delete_user,
    get_user_by_email,
)
from routes.dependencies import normalize_role_name, require_permissions, require_roles
from security.tenant import ensure_workspace_access

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)
ADMIN_CREATE_DEFAULT_ROLE_ID = 1
OTP_EXPIRE_MINUTES = int(os.getenv("REGISTER_OTP_EXPIRE_MINUTES", "10"))
OTP_RESEND_SECONDS = int(os.getenv("REGISTER_OTP_RESEND_SECONDS", "60"))
OTP_SECRET = os.getenv("REGISTER_OTP_SECRET", os.getenv("SECRET_KEY", "change-this-secret-key"))
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SUPER_ADMIN_EMAIL = os.getenv("SUPER_ADMIN_EMAIL", "bahrieveseli1@gmail.com").strip().lower()


def is_admin(user) -> bool:
    return normalize_role_name(user.role.name if user.role else None) == "admin"


def user_role(user: User) -> str:
    return normalize_role_name(user.role.name if user.role else None)


def is_client_user(user: User) -> bool:
    raw_role = (user.role.name if user.role else "").strip().lower()
    return raw_role in {"client", "user"}


def can_manage_clients(user: User) -> bool:
    raw_role = (user.role.name if user.role else "").strip().lower()
    return raw_role in {"admin", "administrator", "employee", "employ"}


def ensure_single_admin(db: Session, role_id: int, user_id: int | None = None) -> None:
    # Multiple admin users are allowed.
    return


def ensure_role_exists(db: Session, role_id: int) -> Role:
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role_id: {role_id}. Role does not exist.",
        )
    return role


def allowed_recipient_roles(sender: User) -> set[str]:
    sender_role = user_role(sender)
    matrix = {
        "admin": {"admin", "employee", "client"},
        "employee": {"admin", "client"},
        "client": {"employee"},
    }
    return matrix.get(sender_role, set())


def hash_otp(email: str, code: str) -> str:
    raw = f"{email.lower().strip()}:{code.strip()}:{OTP_SECRET}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def generate_otp_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


class VerifyInviteOTPRequest(BaseModel):
    email: EmailStr
    code: str


def attach_latest_rating(db: Session, user: User) -> User:
    latest_feedback = (
        db.query(Feedback)
        .filter(Feedback.user_id == user.id)
        .order_by(desc(Feedback.created_at), desc(Feedback.id))
        .first()
    )
    latest_rating_value = latest_feedback.rating if latest_feedback else None

    if latest_rating_value is None:
        latest_rating = (
            db.query(Rating)
            .filter(Rating.user_id == user.id)
            .order_by(desc(Rating.created_at), desc(Rating.id))
            .first()
        )
        latest_rating_value = latest_rating.score if latest_rating else None

    user.last_rate = latest_rating_value
    user.latest_rating = latest_rating_value
    user.rating = latest_rating_value
    user.lastRate = latest_rating_value
    user.latestRating = latest_rating_value

    rating_count, rating_avg = (
        db.query(func.count(Rating.id), func.avg(Rating.score))
        .filter(Rating.user_id == user.id)
        .one()
    )
    feedback_count, feedback_avg = (
        db.query(func.count(Feedback.id), func.avg(Feedback.rating))
        .filter(Feedback.user_id == user.id)
        .one()
    )

    rating_count = int(rating_count or 0)
    feedback_count = int(feedback_count or 0)
    total_count = rating_count + feedback_count

    if total_count > 0:
        weighted_sum = (float(rating_avg or 0) * rating_count) + (float(feedback_avg or 0) * feedback_count)
        user.avg_rating = round(weighted_sum / total_count, 2)
    else:
        user.avg_rating = None
    user.ratings_count = total_count
    user.avgRate = user.avg_rating
    user.ratingsCount = user.ratings_count
    return user


@router.post("/")
def create_user_endpoint(
    data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    if get_user_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    ensure_workspace_access(data.workspace_id, current_user)
    data.role_id = ADMIN_CREATE_DEFAULT_ROLE_ID
    ensure_role_exists(db, data.role_id)
    ensure_single_admin(db, data.role_id)

    now = datetime.now(timezone.utc)
    pending = db.query(RegistrationOTP).filter(RegistrationOTP.email == data.email).first()
    if pending and pending.last_sent_at and (now - pending.last_sent_at).total_seconds() < OTP_RESEND_SECONDS:
        raise HTTPException(
            status_code=429,
            detail=f"Please wait {OTP_RESEND_SECONDS} seconds before requesting a new code",
        )

    code = generate_otp_code()
    code_hash = hash_otp(data.email, code)
    expires_at = now + timedelta(minutes=OTP_EXPIRE_MINUTES)
    password_hash = pwd_context.hash(data.password)

    if pending:
        pending.username = data.username
        pending.full_name = data.full_name
        pending.password_hash = password_hash
        pending.workspace_id = data.workspace_id
        pending.role_id = data.role_id
        pending.otp_hash = code_hash
        pending.attempts = 0
        pending.expires_at = expires_at
        pending.last_sent_at = now
    else:
        pending = RegistrationOTP(
            email=data.email,
            username=data.username,
            full_name=data.full_name,
            password_hash=password_hash,
            workspace_id=data.workspace_id,
            role_id=data.role_id,
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
        "Confirm your employee account",
        f"Your verification code is: {code}. It expires in {OTP_EXPIRE_MINUTES} minutes.",
        current_user.id,
        current_user.workspace_id,
    )
    return {
        "detail": "Employee invitation sent. Account will be created after OTP verification.",
        "role_id": data.role_id,
    }


@router.post("/verify-invite-otp", response_model=UserResponse)
def verify_invite_otp_endpoint(
    data: VerifyInviteOTPRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    existing = get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    pending = db.query(RegistrationOTP).filter(RegistrationOTP.email == data.email).first()
    if not pending:
        raise HTTPException(status_code=404, detail="No pending invite for this email")

    now = datetime.now(timezone.utc)
    expires_at = pending.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < now:
        db.delete(pending)
        db.commit()
        raise HTTPException(status_code=400, detail="Verification code expired")

    if pending.attempts >= 5:
        db.delete(pending)
        db.commit()
        raise HTTPException(status_code=429, detail="Too many invalid attempts. Invite again.")

    if hash_otp(data.email, data.code) != pending.otp_hash:
        pending.attempts += 1
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid verification code")

    user = User(
        full_name=pending.full_name or (pending.username or data.email.split("@")[0]),
        username=pending.username or data.email.split("@")[0],
        email=data.email,
        hashed_password=pending.password_hash,
        workspace_id=pending.workspace_id or current_user.workspace_id,
        role_id=pending.role_id or ADMIN_CREATE_DEFAULT_ROLE_ID,
    )
    db.add(user)
    db.delete(pending)
    db.commit()
    db.refresh(user)
    return user


@router.get("/", response_model=list[UserResponse])
def list_users_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_permissions("view_users")),
):
    users = (
        db.query(User)
        .filter(User.workspace_id == current_user.workspace_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    if not is_admin(current_user):
        users = [user for user in users if is_client_user(user)]
    return [attach_latest_rating(db, user) for user in users]


@router.get("/clients", response_model=list[UserResponse])
def list_clients_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_permissions("view_users")),
):
    if not can_manage_clients(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access client entities",
        )

    users = (
        db.query(User)
        .filter(User.workspace_id == current_user.workspace_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    users = [user for user in users if is_client_user(user)]
    return [attach_latest_rating(db, user) for user in users]


@router.get("/allowed-recipients", response_model=list[AllowedRecipientResponse])
def list_allowed_recipients_endpoint(
    db: Session = Depends(get_db),
    current_user=Depends(require_permissions("view_allowed_recipients")),
):
    if (current_user.email or "").strip().lower() != SUPER_ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Only super admin can view allowed recipients")

    allowed_roles = allowed_recipient_roles(current_user)
    if not allowed_roles:
        return []

    sender_role = user_role(current_user)
    query = db.query(User).filter(User.id != current_user.id)
    if sender_role != "client":
        query = query.filter(User.workspace_id == current_user.workspace_id)
    users = query.all()

    recipients = []
    for user in users:
        role_name = user_role(user)
        if role_name in allowed_roles:
            recipients.append(
                AllowedRecipientResponse(
                    id=user.id,
                    full_name=user.full_name,
                    email=user.email,
                    role_id=user.role_id,
                    role_name=role_name,
                    workspace_id=user.workspace_id,
                )
            )
    return recipients


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
        ensure_role_exists(db, data.role_id)
        ensure_single_admin(db, data.role_id, user_id=user_id)
    db_obj = update_user(db, user_id, data)
    return db_obj


@router.patch("/{user_id}/make-employee", response_model=UserResponse)
def make_employee_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = get_user_by_id(db, user_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="User not found")

    role = db.query(Role).filter(Role.name == "employee").first()
    if role is None:
        role = db.query(Role).filter(Role.id == 1).first()
    if role is None:
        raise HTTPException(status_code=400, detail="Employee role not found")

    db_obj.role_id = role.id
    db.commit()
    db.refresh(db_obj)
    return db_obj


@router.delete("/clients/{user_id}")
def delete_client_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_permissions("delete_user")),
):
    if not can_manage_clients(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete client entities",
        )

    db_obj = get_user_by_id(db, user_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="User not found")
    if not is_client_user(db_obj):
        raise HTTPException(status_code=403, detail="missing permission: delete_user")
    deleted = delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


@router.delete("/me")
def delete_current_user_endpoint(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "employee", "client")),
):
    db_obj = get_user_by_id(db, current_user.id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="User not found")

    # Keep super admin protected from accidental self-removal.
    if (db_obj.email or "").strip().lower() == SUPER_ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Blocked by policy")

    try:
        deleted = delete_user(db, current_user.id)
        if not deleted:
            raise HTTPException(status_code=404, detail="User not found")
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=403, detail="Blocked by policy")

    return {"detail": "Account deleted successfully"}


@router.delete("/{user_id}")
def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_permissions("delete_user")),
):
    db_obj = get_user_by_id(db, user_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="User not found")
    if not is_admin(current_user) and not is_client_user(db_obj):
        raise HTTPException(status_code=403, detail="missing permission: delete_user")
    deleted = delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
