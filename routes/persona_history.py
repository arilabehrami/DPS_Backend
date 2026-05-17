from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.persona_history import PersonaHistoryCreate, PersonaHistoryUpdate, PersonaHistoryResponse
from services.persona_history import (
    create_persona_history,
    get_persona_history,
    get_persona_history_by_id,
    get_persona_history_by_persona_id,
    update_persona_history,
    delete_persona_history
)

router = APIRouter(prefix="/persona-history", tags=["Persona History"])


@router.post("/", response_model=PersonaHistoryResponse)
def create_persona_history_endpoint(data: PersonaHistoryCreate, db: Session = Depends(get_db)):
    return create_persona_history(db, data)


@router.get("/", response_model=list[PersonaHistoryResponse])
def get_persona_history_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_persona_history(db, skip, limit)


@router.get("/{history_id}", response_model=PersonaHistoryResponse)
def get_persona_history_by_id_endpoint(history_id: int, db: Session = Depends(get_db)):
    persona_history = get_persona_history_by_id(db, history_id)

    if not persona_history:
        raise HTTPException(status_code=404, detail="Persona history not found")

    return persona_history


@router.get("/persona/{persona_id}", response_model=list[PersonaHistoryResponse])
def get_persona_history_by_persona_endpoint(persona_id: int, db: Session = Depends(get_db)):
    return get_persona_history_by_persona_id(db, persona_id)


@router.put("/{history_id}", response_model=PersonaHistoryResponse)
def update_persona_history_endpoint(history_id: int, data: PersonaHistoryUpdate, db: Session = Depends(get_db)):
    persona_history = update_persona_history(db, history_id, data)

    if not persona_history:
        raise HTTPException(status_code=404, detail="Persona history not found")

    return persona_history


@router.delete("/{history_id}")
def delete_persona_history_endpoint(history_id: int, db: Session = Depends(get_db)):
    persona_history = delete_persona_history(db, history_id)

    if not persona_history:
        raise HTTPException(status_code=404, detail="Persona history not found")

    return {"message": "Persona history deleted successfully"}