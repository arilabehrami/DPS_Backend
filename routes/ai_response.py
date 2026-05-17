from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.ai_response import AIResponseCreate, AIResponseUpdate, AIResponseResponse
from services.ai_response import (
    create_ai_response,
    get_ai_responses,
    get_ai_response_by_id,
    get_ai_responses_by_message_id,
    update_ai_response,
    delete_ai_response
)

router = APIRouter(prefix="/ai-responses", tags=["AI Responses"])


@router.post("/", response_model=AIResponseResponse)
def create_ai_response_endpoint(data: AIResponseCreate, db: Session = Depends(get_db)):
    return create_ai_response(db, data)


@router.get("/", response_model=list[AIResponseResponse])
def get_ai_responses_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_ai_responses(db, skip, limit)


@router.get("/{ai_response_id}", response_model=AIResponseResponse)
def get_ai_response_endpoint(ai_response_id: int, db: Session = Depends(get_db)):
    ai_response = get_ai_response_by_id(db, ai_response_id)

    if not ai_response:
        raise HTTPException(status_code=404, detail="AI response not found")

    return ai_response


@router.get("/message/{message_id}", response_model=list[AIResponseResponse])
def get_ai_responses_by_message_endpoint(message_id: int, db: Session = Depends(get_db)):
    return get_ai_responses_by_message_id(db, message_id)


@router.put("/{ai_response_id}", response_model=AIResponseResponse)
def update_ai_response_endpoint(ai_response_id: int, data: AIResponseUpdate, db: Session = Depends(get_db)):
    ai_response = update_ai_response(db, ai_response_id, data)

    if not ai_response:
        raise HTTPException(status_code=404, detail="AI response not found")

    return ai_response


@router.delete("/{ai_response_id}")
def delete_ai_response_endpoint(ai_response_id: int, db: Session = Depends(get_db)):
    ai_response = delete_ai_response(db, ai_response_id)

    if not ai_response:
        raise HTTPException(status_code=404, detail="AI response not found")

    return {"message": "AI response deleted successfully"}