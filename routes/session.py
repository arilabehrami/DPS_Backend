from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models.session import Session as DBSession

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_sessions(db: Session = Depends(get_db)):
    return db.query(DBSession).all()


@router.get("/{session_id}")
def get_session(session_id: int, db: Session = Depends(get_db)):
    return db.query(DBSession).filter(DBSession.id == session_id).first()