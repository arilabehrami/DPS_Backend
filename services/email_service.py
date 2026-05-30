import os
import smtplib
from email.message import EmailMessage


def _as_bool(value: str | None, default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def send_email(
    to_email: str,
    subject: str,
    content: str,
    reply_to: str | None = None,
    sender_display: str | None = None,
) -> None:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM", user or "")
    use_tls = _as_bool(os.getenv("SMTP_TLS"), default=True)

    if not host or not sender:
        raise ValueError("SMTP is not configured. Set SMTP_HOST and SMTP_FROM (or SMTP_USER).")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = to_email
    if reply_to:
        message["Reply-To"] = reply_to
    if sender_display:
        message["X-Sent-By-User"] = sender_display
    message.set_content(content)

    with smtplib.SMTP(host, port, timeout=20) as server:
        if use_tls:
            server.starttls()
        if user and password:
            server.login(user, password)
        server.send_message(message)
