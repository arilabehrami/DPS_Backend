from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)

    # FIX: duhet hashed_password (jo password)
    hashed_password = Column(String, nullable=False)

    workspace = relationship("Workspace", back_populates="users")
    role = relationship("Role", back_populates="users")

    personas = relationship("Persona", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")

    notifications = relationship("Notification")
    feedbacks = relationship("Feedback")
    sessions = relationship("Session")