from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class PersonaTrait(Base):
    __tablename__ = "persona_traits"

    id = Column(Integer, primary_key=True, index=True)
    personality_id = Column(Integer, ForeignKey("personalities.id"), nullable=False)
    trait_name = Column(String, nullable=False)
    trait_value = Column(String, nullable=False)

    personality = relationship("Personality", back_populates="traits")
