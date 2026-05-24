from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class InteractionStat(Base):
    __tablename__ = "interaction_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    personality_id = Column(Integer, ForeignKey("personalities.id"), nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    total_messages = Column(Integer, default=0, nullable=False)
    last_interaction = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="interaction_stats")
    personality = relationship("Personality", back_populates="interaction_stats")
    workspace = relationship("Workspace", back_populates="interaction_stats")
    conversation = relationship("Conversation", back_populates="interaction_stats")
