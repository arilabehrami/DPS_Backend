from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    users = relationship("User", back_populates="workspace", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="workspace", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="workspace")
    event_logs = relationship("EventLog", back_populates="workspace")
    interaction_stats = relationship("InteractionStat", back_populates="workspace", cascade="all, delete-orphan")
    personas = relationship("Persona", back_populates="workspace", cascade="all, delete-orphan")
    personalities = relationship("Personality", back_populates="workspace", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="workspace", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="workspace", cascade="all, delete-orphan")
    settings = relationship("Setting", back_populates="workspace")
    experiments = relationship("Experiment", back_populates="workspace", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="workspace", cascade="all, delete-orphan")
