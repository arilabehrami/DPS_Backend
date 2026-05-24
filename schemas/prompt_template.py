from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PromptTemplateBase(BaseModel):
    persona_id: int
    template_text: str


class PromptTemplateCreate(PromptTemplateBase):
    pass


class PromptTemplateUpdate(BaseModel):
    persona_id: Optional[int] = None
    template_text: Optional[str] = None


class PromptTemplateResponse(PromptTemplateBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
