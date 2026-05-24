from sqlalchemy.orm import Session
from models.rating import Rating
from schemas.rating import RatingCreate, RatingUpdate


def create_rating(db: Session, data: RatingCreate) -> Rating:
    db_obj = Rating(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_rating_by_id(db: Session, rating_id: int) -> Rating | None:
    return db.query(Rating).filter(Rating.id == rating_id).first()


def get_ratings(db: Session, skip: int = 0, limit: int = 100) -> list[Rating]:
    return db.query(Rating).offset(skip).limit(limit).all()


def update_rating(db: Session, rating_id: int, data: RatingUpdate) -> Rating | None:
    db_obj = get_rating_by_id(db, rating_id)
    if not db_obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_rating(db: Session, rating_id: int) -> bool:
    db_obj = get_rating_by_id(db, rating_id)
    if not db_obj:
        return False

    db.delete(db_obj)
    db.commit()
    return True
