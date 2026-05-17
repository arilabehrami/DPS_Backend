from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.prompt_template import PromptTemplateCreate, PromptTemplateUpdate, PromptTemplateResponse
from services.prompt_template import (
    create_prompt_template,
    get_prompt_templates,
    get_prompt_template_by_id,
    search_prompt_templates,
    update_prompt_template,
    delete_prompt_template
)

router = APIRouter(prefix="/prompt-templates", tags=["Prompt Templates"])


@router.post("/", response_model=PromptTemplateResponse)
def create_prompt_template_endpoint(data: PromptTemplateCreate, db: Session = Depends(get_db)):
    return create_prompt_template(db, data)


@router.get("/", response_model=list[PromptTemplateResponse])
def get_prompt_templates_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_prompt_templates(db, skip, limit)


@router.get("/search", response_model=list[PromptTemplateResponse])
def search_prompt_templates_endpoint(keyword: str, db: Session = Depends(get_db)):
    return search_prompt_templates(db, keyword)


@router.get("/{template_id}", response_model=PromptTemplateResponse)
def get_prompt_template_endpoint(template_id: int, db: Session = Depends(get_db)):
    prompt_template = get_prompt_template_by_id(db, template_id)

    if not prompt_template:
        raise HTTPException(status_code=404, detail="Prompt template not found")

    return prompt_template


@router.put("/{template_id}", response_model=PromptTemplateResponse)
def update_prompt_template_endpoint(template_id: int, data: PromptTemplateUpdate, db: Session = Depends(get_db)):
    prompt_template = update_prompt_template(db, template_id, data)

    if not prompt_template:
        raise HTTPException(status_code=404, detail="Prompt template not found")

    return prompt_template


@router.delete("/{template_id}")
def delete_prompt_template_endpoint(template_id: int, db: Session = Depends(get_db)):
    prompt_template = delete_prompt_template(db, template_id)

    if not prompt_template:
        raise HTTPException(status_code=404, detail="Prompt template not found")

    return {"message": "Prompt template deleted successfully"}