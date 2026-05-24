from sqlalchemy.orm import Session
from models.interaction_stat import InteractionStat
from schemas.interaction_stat import InteractionStatCreate, InteractionStatUpdate


def create_interaction_stat(db: Session, data: InteractionStatCreate) -> InteractionStat:
    db_obj = InteractionStat(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_interaction_stat_by_id(db: Session, interaction_stat_id: int) -> InteractionStat | None:
    return db.query(InteractionStat).filter(InteractionStat.id == interaction_stat_id).first()


def get_interaction_stats(db: Session, skip: int = 0, limit: int = 100) -> list[InteractionStat]:
    return db.query(InteractionStat).offset(skip).limit(limit).all()


def update_interaction_stat(db: Session, interaction_stat_id: int, data: InteractionStatUpdate) -> InteractionStat | None:
    db_obj = get_interaction_stat_by_id(db, interaction_stat_id)
    if not db_obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_interaction_stat(db: Session, interaction_stat_id: int) -> bool:
    db_obj = get_interaction_stat_by_id(db, interaction_stat_id)
    if not db_obj:
        return False

    db.delete(db_obj)
    db.commit()
    return True
