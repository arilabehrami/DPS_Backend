from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class PersonaTrait(Base):
    __tablename__ = "persona_traits"

    id = Column(Integer, primary_key=True, index=True)
    persona_id = Column(Integer, ForeignKey("personas.id"))
    
    trait_name = Column(String, nullable=False)   # p.sh "CEO strict"
    value = Column(String, nullable=True)