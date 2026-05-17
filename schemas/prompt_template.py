from pydantic import BaseModel


class PromptTemplateCreate(BaseModel):
    name: str
    template: str


class PromptTemplateResponse(BaseModel):
    id: int
    name: str
    template: str

    class Config:
        from_attributes = True