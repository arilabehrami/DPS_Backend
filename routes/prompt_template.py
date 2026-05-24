from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas.prompt_template import PromptTemplateCreate, PromptTemplateUpdate, PromptTemplateResponse
from services.prompt_template import (
    create_prompt_template,
    get_prompt_template_by_id,
    get_prompt_templates,
    update_prompt_template,
    delete_prompt_template,
)
from routes.dependencies import require_roles

router = APIRouter(
    prefix="/prompt-templates",
    tags=["Prompt Templates"],
)


@router.post("/", response_model=PromptTemplateResponse)
def create_prompt_template_endpoint(
    data: PromptTemplateCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    return create_prompt_template(db, data)


@router.get("/", response_model=list[PromptTemplateResponse])
def list_prompt_templates_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return get_prompt_templates(db, skip=skip, limit=limit)


@router.get("/{prompt_template_id}", response_model=PromptTemplateResponse)
def get_prompt_template_endpoint(
    prompt_template_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_prompt_template_by_id(db, prompt_template_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="PromptTemplate not found")
    return db_obj


@router.put("/{prompt_template_id}", response_model=PromptTemplateResponse)
def update_prompt_template_endpoint(
    prompt_template_id: int,
    data: PromptTemplateUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = update_prompt_template(db, prompt_template_id, data)
    if not db_obj:
        raise HTTPException(status_code=404, detail="PromptTemplate not found")
    return db_obj


@router.delete("/{prompt_template_id}")
def delete_prompt_template_endpoint(
    prompt_template_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    deleted = delete_prompt_template(db, prompt_template_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="PromptTemplate not found")
    return {"message": "PromptTemplate deleted successfully"}
