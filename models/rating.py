from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    personality_id = Column(Integer, ForeignKey("personalities.id"), nullable=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    score = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="ratings")
    personality = relationship("Personality", back_populates="ratings")
    conversation = relationship("Conversation", back_populates="ratings")
    workspace = relationship("Workspace", back_populates="ratings")
