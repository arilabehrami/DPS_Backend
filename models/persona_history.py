from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, String
from datetime import datetime
from database import Base

class PersonaHistory(Base):
    __tablename__ = "persona_history"

    id = Column(Integer, primary_key=True, index=True)

    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=False)
    changed_field = Column(String, nullable=True)  # p.sh. tone, behavior

    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)

    changed_at = Column(DateTime, default=datetime.utcnow)