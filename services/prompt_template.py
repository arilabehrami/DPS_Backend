from sqlalchemy.orm import Session
from models.prompt_template import PromptTemplate
from schemas.prompt_template import PromptTemplateCreate, PromptTemplateUpdate


def create_prompt_template(db: Session, data: PromptTemplateCreate):
    prompt_template = PromptTemplate(**data.dict(exclude_unset=True))
    db.add(prompt_template)
    db.commit()
    db.refresh(prompt_template)
    return prompt_template


def get_prompt_templates(db: Session, skip: int = 0, limit: int = 100):
    return db.query(PromptTemplate).offset(skip).limit(limit).all()


def get_prompt_template_by_id(db: Session, template_id: int):
    return db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()


def search_prompt_templates(db: Session, keyword: str):
    return db.query(PromptTemplate).filter(PromptTemplate.name.ilike(f"%{keyword}%")).all()


def update_prompt_template(db: Session, template_id: int, data: PromptTemplateUpdate):
    prompt_template = get_prompt_template_by_id(db, template_id)

    if not prompt_template:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(prompt_template, field, value)

    db.commit()
    db.refresh(prompt_template)
    return prompt_template


def delete_prompt_template(db: Session, template_id: int):
    prompt_template = get_prompt_template_by_id(db, template_id)

    if not prompt_template:
        return None

    db.delete(prompt_template)
    db.commit()
    return prompt_template