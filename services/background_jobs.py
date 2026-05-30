import hashlib

from database import SessionLocal
from models.email_send_audit import EmailSendAudit
from models.event_log import EventLog
from models.user import User
from services.email_service import send_email


def record_event_log(user_id: int | None, workspace_id: int | None, event_type: str, description: str) -> None:
    # event_logs.user_id is NOT NULL; skip system-level events without actor user.
    if user_id is None:
        return

    db = SessionLocal()
    try:
        user_exists = db.query(User.id).filter(User.id == user_id).first()
        if not user_exists:
            return

        db.add(
            EventLog(
                user_id=user_id,
                workspace_id=workspace_id,
                event_type=event_type,
                description=description,
            )
        )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def record_email_audit(
    sender_id: int | None,
    recipient_id: int | None,
    workspace_id: int | None,
    subject: str,
    status: str,
) -> None:
    db = SessionLocal()
    try:
        if sender_id is not None:
            sender_exists = db.query(User.id).filter(User.id == sender_id).first()
            if not sender_exists:
                sender_id = None

        if recipient_id is not None:
            recipient_exists = db.query(User.id).filter(User.id == recipient_id).first()
            if not recipient_exists:
                recipient_id = None

        db.add(
            EmailSendAudit(
                sender_id=sender_id,
                recipient_id=recipient_id,
                workspace_id=workspace_id,
                subject_hash=hashlib.sha256(subject.encode("utf-8")).hexdigest()[:24] if subject else None,
                subject_length=len(subject or ""),
                status=status,
            )
        )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def send_email_job(
    to_email: str,
    subject: str,
    content: str,
    requested_by_user_id: int | None = None,
    workspace_id: int | None = None,
    reply_to: str | None = None,
    sender_display: str | None = None,
    recipient_user_id: int | None = None,
) -> None:
    try:
        send_email(
            to_email,
            subject,
            content,
            reply_to=reply_to,
            sender_display=sender_display,
        )
        record_email_audit(
            requested_by_user_id,
            recipient_user_id,
            workspace_id,
            subject,
            "sent",
        )
        record_event_log(
            requested_by_user_id,
            workspace_id,
            "email_sent",
            f"Email sent to {to_email}: {subject} (reply-to: {reply_to or 'none'})",
        )
    except Exception as exc:
        record_email_audit(
            requested_by_user_id,
            recipient_user_id,
            workspace_id,
            subject,
            "failed",
        )
        record_event_log(
            requested_by_user_id,
            workspace_id,
            "email_failed",
            f"Email failed to {to_email}: {subject}. Error: {exc}",
        )
