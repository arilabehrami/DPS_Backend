from sqlalchemy.orm import Session
from models.prompt_template import PromptTemplate
from schemas.prompt_template import PromptTemplateCreate, PromptTemplateUpdate


def create_prompt_template(db: Session, data: PromptTemplateCreate) -> PromptTemplate:
    db_obj = PromptTemplate(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_prompt_template_by_id(db: Session, prompt_template_id: int) -> PromptTemplate | None:
    return db.query(PromptTemplate).filter(PromptTemplate.id == prompt_template_id).first()


def get_prompt_templates(db: Session, skip: int = 0, limit: int = 100) -> list[PromptTemplate]:
    return db.query(PromptTemplate).offset(skip).limit(limit).all()


def update_prompt_template(db: Session, prompt_template_id: int, data: PromptTemplateUpdate) -> PromptTemplate | None:
    db_obj = get_prompt_template_by_id(db, prompt_template_id)
    if not db_obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_prompt_template(db: Session, prompt_template_id: int) -> bool:
    db_obj = get_prompt_template_by_id(db, prompt_template_id)
    if not db_obj:
        return False

    db.delete(db_obj)
    db.commit()
    return True
