from sqlalchemy.orm import Session
from models.ai_response import AIResponse
from schemas.ai_response import AIResponseCreate, AIResponseUpdate


def create_ai_response(db: Session, data: AIResponseCreate):
    ai_response = AIResponse(**data.dict(exclude_unset=True))
    db.add(ai_response)
    db.commit()
    db.refresh(ai_response)
    return ai_response


def get_ai_responses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(AIResponse).offset(skip).limit(limit).all()


def get_ai_response_by_id(db: Session, ai_response_id: int):
    return db.query(AIResponse).filter(AIResponse.id == ai_response_id).first()


def get_ai_responses_by_message_id(db: Session, message_id: int):
    return db.query(AIResponse).filter(AIResponse.message_id == message_id).all()


def update_ai_response(db: Session, ai_response_id: int, data: AIResponseUpdate):
    ai_response = get_ai_response_by_id(db, ai_response_id)

    if not ai_response:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(ai_response, field, value)

    db.commit()
    db.refresh(ai_response)
    return ai_response


def delete_ai_response(db: Session, ai_response_id: int):
    ai_response = get_ai_response_by_id(db, ai_response_id)

    if not ai_response:
        return None

    db.delete(ai_response)
    db.commit()
    return ai_response