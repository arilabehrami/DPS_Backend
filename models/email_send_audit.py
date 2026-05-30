from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from database import Base


class EmailSendAudit(Base):
    __tablename__ = "email_send_audits"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    workspace_id = Column(Integer, nullable=True, index=True)
    subject_hash = Column(String, nullable=True)
    subject_length = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False)  # queued | sent | failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
