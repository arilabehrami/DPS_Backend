from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models.ai_response import AIResponse

router = APIRouter(
    prefix="/ai-responses",
    tags=["AI Responses"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_ai_responses(db: Session = Depends(get_db)):
    return db.query(AIResponse).all()


@router.get("/{response_id}")
def get_ai_response(response_id: int, db: Session = Depends(get_db)):
    return db.query(AIResponse).filter(
        AIResponse.id == response_id
    ).first()