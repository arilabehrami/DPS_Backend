from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Personality(Base):
    __tablename__ = "personalities"

    id = Column(Integer, primary_key=True, index=True)
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    persona = relationship("Persona", back_populates="personalities")
    user = relationship("User", back_populates="personalities")
    workspace = relationship("Workspace", back_populates="personalities")
    traits = relationship("PersonaTrait", back_populates="personality", cascade="all, delete-orphan")
    history = relationship("PersonaHistory", back_populates="personality", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="personality", cascade="all, delete-orphan")
    sent_messages = relationship("Message", back_populates="sender_personality", foreign_keys="Message.sender_personality_id")
    interaction_stats = relationship("InteractionStat", back_populates="personality")
    experiments = relationship("Experiment", back_populates="personality")
    ratings = relationship("Rating", back_populates="personality", cascade="all, delete-orphan")
