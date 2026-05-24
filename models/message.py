from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    sender_type = Column(String, nullable=False)  # user, personality, system
    sender_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sender_personality_id = Column(Integer, ForeignKey("personalities.id"), nullable=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")
    workspace = relationship("Workspace", back_populates="messages")
    sender_user = relationship("User", back_populates="sent_messages", foreign_keys=[sender_user_id])
    sender_personality = relationship("Personality", back_populates="sent_messages", foreign_keys=[sender_personality_id])
