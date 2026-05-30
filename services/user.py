from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models.audit_log import AuditLog
from models.email_message import EmailMessage
from models.email_send_audit import EmailSendAudit
from models.event_log import EventLog
from models.user import User
from schemas.user import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_user(db: Session, data: UserCreate) -> User:
    payload = data.model_dump()
    plain_password = payload.pop("password")
    db_obj = User(**payload, hashed_password=hash_password(plain_password))
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_users_by_workspace_id(db: Session, workspace_id: int) -> list[User]:
    return db.query(User).filter(User.workspace_id == workspace_id).all()


def get_users_by_role_id(db: Session, role_id: int) -> list[User]:
    return db.query(User).filter(User.role_id == role_id).all()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, data: UserUpdate) -> User | None:
    db_obj = get_user_by_id(db, user_id)
    if not db_obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_user(db: Session, user_id: int) -> bool:
    db_obj = get_user_by_id(db, user_id)
    if not db_obj:
        return False

    # Keep FK constraints happy on schemas where logs require non-null user_id.
    db.query(EmailMessage).filter(
        (EmailMessage.sender_user_id == user_id) | (EmailMessage.recipient_user_id == user_id)
    ).delete(synchronize_session=False)
    db.query(EmailSendAudit).filter(
        (EmailSendAudit.sender_id == user_id) | (EmailSendAudit.recipient_id == user_id)
    ).delete(synchronize_session=False)
    db.query(EventLog).filter(EventLog.user_id == user_id).delete(synchronize_session=False)
    db.query(AuditLog).filter(AuditLog.user_id == user_id).delete(synchronize_session=False)
    db.delete(db_obj)
    db.commit()
    return True
