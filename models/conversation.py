from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    personality_id = Column(Integer, ForeignKey("personalities.id"))
    title = Column(String, nullable=True)
    status = Column(String, nullable=True)

    user = relationship("User", back_populates="conversations")
    personality = relationship("Personality", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")
