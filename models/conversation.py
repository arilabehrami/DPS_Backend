from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    workspace_id = Column(
        Integer,
        ForeignKey("workspaces.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    persona_id = Column(
        Integer,
        ForeignKey("personas.id"),
        nullable=False
    )

    title = Column(String)

    user = relationship(
        "User",
        back_populates="conversations"
    )

    persona = relationship(
        "Persona",
        back_populates="conversations"
    )

    messages = relationship(
        "Message",
        back_populates="conversation"
    )