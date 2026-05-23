from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.ai_response import AIResponse
from models.message import Message
from models.user import User
from security.auth_security import get_current_user
from security.tenant import ensure_message_access
from schemas.ai_response import AIResponseCreate, AIResponseUpdate, AIResponseResponse
from services.ai_response import (
    create_ai_response,
    get_ai_responses,
    get_ai_response_by_id,
    get_ai_responses_by_message_id,
    update_ai_response,
    delete_ai_response
)

router = APIRouter(
    prefix="/ai-responses",
    tags=["AI Responses"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=AIResponseResponse)
def create_ai_response_endpoint(
    data: AIResponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.message_id is not None:
        ensure_message_access(db, data.message_id, current_user)
    return create_ai_response(db, data)


@router.get("/", response_model=list[AIResponseResponse])
def get_ai_responses_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(AIResponse)
        .join(Message, AIResponse.message_id == Message.id)
        .filter(Message.workspace_id == current_user.workspace_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{ai_response_id}", response_model=AIResponseResponse)
def get_ai_response_endpoint(
    ai_response_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ai_response = get_ai_response_by_id(db, ai_response_id)

    if not ai_response:
        raise HTTPException(status_code=404, detail="AI response not found")

    if ai_response.message_id is not None:
        ensure_message_access(db, ai_response.message_id, current_user)

    return ai_response


@router.get("/message/{message_id}", response_model=list[AIResponseResponse])
def get_ai_responses_by_message_endpoint(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_message_access(db, message_id, current_user)
    return get_ai_responses_by_message_id(db, message_id)


@router.put("/{ai_response_id}", response_model=AIResponseResponse)
def update_ai_response_endpoint(
    ai_response_id: int,
    data: AIResponseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ai_response = get_ai_response_by_id(db, ai_response_id)
    if not ai_response:
        raise HTTPException(status_code=404, detail="AI response not found")

    if ai_response.message_id is not None:
        ensure_message_access(db, ai_response.message_id, current_user)
    if data.message_id is not None:
        ensure_message_access(db, data.message_id, current_user)

    ai_response = update_ai_response(db, ai_response_id, data)

    if not ai_response:
        raise HTTPException(status_code=404, detail="AI response not found")

    return ai_response


@router.delete("/{ai_response_id}")
def delete_ai_response_endpoint(
    ai_response_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ai_response = get_ai_response_by_id(db, ai_response_id)
    if not ai_response:
        raise HTTPException(status_code=404, detail="AI response not found")

    if ai_response.message_id is not None:
        ensure_message_access(db, ai_response.message_id, current_user)

    ai_response = delete_ai_response(db, ai_response_id)

    if not ai_response:
        raise HTTPException(status_code=404, detail="AI response not found")

    return {"message": "AI response deleted successfully"}
