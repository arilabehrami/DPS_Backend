from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class PromptTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    template: str


class PromptTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template: Optional[str] = None


class PromptTemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    template: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True