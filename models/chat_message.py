from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from datetime import datetime
from database import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    sender = Column(String)  # user / ai
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    created_at = Column(DateTime, default=datetime.utcnow)