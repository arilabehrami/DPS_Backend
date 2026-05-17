from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    title = Column(String)

    is_read = Column(Boolean, default=False)