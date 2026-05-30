from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
import os
import time
from typing import Annotated

from pydantic import BaseModel, StringConstraints
from sqlalchemy import desc
from sqlalchemy.orm import Session

from database import get_db
from models.email_message import EmailMessage
from models.user import User
from routes.dependencies import normalize_role_name, require_roles
from services.background_jobs import record_email_audit, send_email_job

router = APIRouter(prefix="/background-jobs", tags=["Background Jobs"])
SUPER_ADMIN_EMAIL = os.getenv("SUPER_ADMIN_EMAIL", "bahrieveseli1@gmail.com").strip().lower()
EMAIL_SEND_RATE_LIMIT = int(os.getenv("EMAIL_SEND_RATE_LIMIT", "20"))
EMAIL_SEND_RATE_WINDOW_SECONDS = int(os.getenv("EMAIL_SEND_RATE_WINDOW_SECONDS", "60"))
_send_rate_bucket: dict[int, list[float]] = {}

NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class RoleBasedEmailRequest(BaseModel):
    recipient_user_id: int
    subject: NonEmptyText
    content: NonEmptyText


class EmailInboxItem(BaseModel):
    id: int
    sender_email: str
    subject: str
    content: str
    created_at: str


def can_send_email(sender_role: str, recipient_role: str) -> bool:
    allowed = {
        "admin": {"admin", "employee", "client"},
        "employee": {"admin", "client"},
        "client": {"employee"},
    }
    return recipient_role in allowed.get(sender_role, set())


def enforce_send_rate_limit(user_id: int) -> None:
    now = time.time()
    history = _send_rate_bucket.get(user_id, [])
    history = [ts for ts in history if now - ts < EMAIL_SEND_RATE_WINDOW_SECONDS]
    if len(history) >= EMAIL_SEND_RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: max {EMAIL_SEND_RATE_LIMIT} emails per {EMAIL_SEND_RATE_WINDOW_SECONDS} seconds",
        )
    history.append(now)
    _send_rate_bucket[user_id] = history


@router.post("/email/send")
def queue_role_based_email(
    data: RoleBasedEmailRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    if (current_user.email or "").strip().lower() != SUPER_ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Only super admin can send emails")
    enforce_send_rate_limit(current_user.id)

    sender_role = normalize_role_name(current_user.role.name if current_user.role else None)
    base_query = db.query(User).filter(User.id == data.recipient_user_id)
    if sender_role != "client":
        base_query = base_query.filter(User.workspace_id == current_user.workspace_id)
    recipient = base_query.first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient user not found in your workspace")

    recipient_role = normalize_role_name(recipient.role.name if recipient.role else None)

    if not can_send_email(sender_role, recipient_role):
        raise HTTPException(
            status_code=403,
            detail="Email policy violation: not allowed recipient role",
        )

    body_content = f"Sent by: {current_user.full_name} <{current_user.email}>\n\n{data.content}"
    email_row = EmailMessage(
        sender_user_id=current_user.id,
        recipient_user_id=recipient.id,
        workspace_id=current_user.workspace_id,
        subject=data.subject,
        content=body_content,
    )
    db.add(email_row)
    db.commit()

    try:
        background_tasks.add_task(
            send_email_job,
            recipient.email,
            data.subject,
            body_content,
            current_user.id,
            current_user.workspace_id,
            current_user.email,
            current_user.full_name,
            recipient.id,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Email queue unavailable: {exc}")
    record_email_audit(
        current_user.id,
        recipient.id,
        current_user.workspace_id,
        data.subject,
        "queued",
    )
    return {"detail": "Email queued successfully"}


@router.get("/email/inbox", response_model=list[EmailInboxItem])
def email_inbox(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "employee", "client")),
):
    rows = (
        db.query(EmailMessage, User.email)
        .join(User, User.id == EmailMessage.sender_user_id)
        .filter(EmailMessage.recipient_user_id == current_user.id)
        .order_by(desc(EmailMessage.created_at), desc(EmailMessage.id))
        .all()
    )
    response: list[EmailInboxItem] = []
    for message_row, sender_email in rows:
        response.append(
            EmailInboxItem(
                id=message_row.id,
                sender_email=sender_email,
                subject=message_row.subject,
                content=message_row.content,
                created_at=message_row.created_at.isoformat().replace("+00:00", "Z")
                if message_row.created_at
                else "",
            )
        )
    return response


@router.delete("/email/inbox/{id}")
def delete_email_inbox_message(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "employee", "client")),
):
    message = (
        db.query(EmailMessage)
        .filter(
            EmailMessage.id == id,
            EmailMessage.recipient_user_id == current_user.id,
        )
        .first()
    )
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    db.delete(message)
    db.commit()
    return {"detail": "Message deleted successfully"}
