from sqlalchemy.orm import Session
from models.interaction_stats import InteractionStats
from schemas.interaction_stats import InteractionStatsCreate, InteractionStatsUpdate


def create_interaction_stats(db: Session, data: InteractionStatsCreate):
    interaction_stats = InteractionStats(**data.dict(exclude_unset=True))
    db.add(interaction_stats)
    db.commit()
    db.refresh(interaction_stats)
    return interaction_stats


def get_interaction_stats(db: Session, skip: int = 0, limit: int = 100):
    return db.query(InteractionStats).offset(skip).limit(limit).all()


def get_interaction_stats_by_id(db: Session, stats_id: int):
    return db.query(InteractionStats).filter(InteractionStats.id == stats_id).first()


def get_interaction_stats_by_user_id(db: Session, user_id: int):
    return db.query(InteractionStats).filter(InteractionStats.user_id == user_id).all()


def get_interaction_stats_by_persona_id(db: Session, persona_id: int):
    return db.query(InteractionStats).filter(InteractionStats.persona_id == persona_id).all()


def update_interaction_stats(db: Session, stats_id: int, data: InteractionStatsUpdate):
    interaction_stats = get_interaction_stats_by_id(db, stats_id)

    if not interaction_stats:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(interaction_stats, field, value)

    db.commit()
    db.refresh(interaction_stats)
    return interaction_stats


def delete_interaction_stats(db: Session, stats_id: int):
    interaction_stats = get_interaction_stats_by_id(db, stats_id)

    if not interaction_stats:
        return None

    db.delete(interaction_stats)
    db.commit()
    return interaction_stats