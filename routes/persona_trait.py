from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models.persona_trait import PersonaTrait

router = APIRouter(
    prefix="/persona-traits",
    tags=["Persona Traits"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_traits(db: Session = Depends(get_db)):
    return db.query(PersonaTrait).all()


@router.get("/{trait_id}")
def get_trait(trait_id: int, db: Session = Depends(get_db)):
    return db.query(PersonaTrait).filter(
        PersonaTrait.id == trait_id
    ).first()