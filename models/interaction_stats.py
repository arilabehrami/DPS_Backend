from sqlalchemy import Column, Integer, ForeignKey, DateTime
from datetime import datetime
from database import Base


class InteractionStats(Base):
    __tablename__ = "interaction_stats"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=True)

    total_messages = Column(Integer, default=0)
    total_sessions = Column(Integer, default=0)

    last_interaction = Column(DateTime, default=datetime.utcnow)