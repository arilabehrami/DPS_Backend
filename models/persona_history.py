from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class PersonaHistory(Base):
    __tablename__ = "persona_history"

    id = Column(Integer, primary_key=True, index=True)
    personality_id = Column(Integer, ForeignKey("personalities.id"), nullable=False)
    change_description = Column(Text, nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())

    personality = relationship("Personality", back_populates="history")
