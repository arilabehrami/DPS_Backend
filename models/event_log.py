from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String)
    description = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)