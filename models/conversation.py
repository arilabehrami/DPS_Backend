from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    personality_id = Column(
        Integer,
        ForeignKey("personalities.id"),
        nullable=False
    )

    title = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="conversations")

    personality = relationship(
        "Personality",
        back_populates="conversations"
    )

    messages = relationship(
        "Message",
        back_populates="conversation"
    )