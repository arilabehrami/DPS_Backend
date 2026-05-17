from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime
from database import Base

class AIResponse(Base):
    __tablename__ = "ai_responses"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"))
    
    response_text = Column(Text, nullable=False)
    model_used = Column(String, default="gpt-neo-125M")

    created_at = Column(DateTime, default=datetime.utcnow)