from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime

from database import Base   # 👈 KJO KA MUNGUAR

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    message = Column(String, nullable=False)
    rating = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)