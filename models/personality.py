from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Personality(Base):
    __tablename__ = "personalities"

    id = Column(Integer, primary_key=True, index=True)

    workspace_id = Column(
        Integer,
        ForeignKey("workspaces.id"),
        nullable=False
    )

    name = Column(String, nullable=False)

    description = Column(String)

    user_id = Column(Integer, ForeignKey("users.id"))

    workspace = relationship("Workspace")