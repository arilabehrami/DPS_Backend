from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.message import Message
from schemas.message import MessageCreate, MessageResponse

router = APIRouter(
    prefix="/messages",
    tags=["Messages"]
)


@router.post("/", response_model=MessageResponse)
def create_message(
    message_data: MessageCreate,
    db: Session = Depends(get_db)
):
    message = Message(**message_data.model_dump())

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


@router.get("/", response_model=list[MessageResponse])
def get_messages(db: Session = Depends(get_db)):
    return db.query(Message).all()