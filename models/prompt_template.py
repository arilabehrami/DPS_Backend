from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)  # p.sh. "Friendly AI"
    description = Column(Text, nullable=True)

    template = Column(Text, nullable=False)  # prompt-i kryesor

    created_at = Column(DateTime, default=datetime.utcnow)