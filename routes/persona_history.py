from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.persona import Persona
from models.persona_history import PersonaHistory
from models.user import User
from security.auth_security import get_current_user
from security.tenant import ensure_persona_access, ensure_persona_history_access
from schemas.persona_history import PersonaHistoryCreate, PersonaHistoryUpdate, PersonaHistoryResponse
from services.persona_history import (
    create_persona_history,
    get_persona_history,
    get_persona_history_by_id,
    get_persona_history_by_persona_id,
    update_persona_history,
    delete_persona_history
)

router = APIRouter(
    prefix="/persona-history",
    tags=["Persona History"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=PersonaHistoryResponse)
def create_persona_history_endpoint(
    data: PersonaHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_persona_access(db, data.persona_id, current_user)
    return create_persona_history(db, data)


@router.get("/", response_model=list[PersonaHistoryResponse])
def get_persona_history_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(PersonaHistory)
        .join(Persona, PersonaHistory.persona_id == Persona.id)
        .filter(Persona.workspace_id == current_user.workspace_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{history_id}", response_model=PersonaHistoryResponse)
def get_persona_history_by_id_endpoint(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ensure_persona_history_access(db, history_id, current_user)


@router.get("/persona/{persona_id}", response_model=list[PersonaHistoryResponse])
def get_persona_history_by_persona_endpoint(
    persona_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_persona_access(db, persona_id, current_user)
    return get_persona_history_by_persona_id(db, persona_id)


@router.put("/{history_id}", response_model=PersonaHistoryResponse)
def update_persona_history_endpoint(
    history_id: int,
    data: PersonaHistoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_persona_history_access(db, history_id, current_user)
    persona_history = update_persona_history(db, history_id, data)

    if not persona_history:
        raise HTTPException(status_code=404, detail="Persona history not found")

    return persona_history


@router.delete("/{history_id}")
def delete_persona_history_endpoint(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_persona_history_access(db, history_id, current_user)
    persona_history = delete_persona_history(db, history_id)

    if not persona_history:
        raise HTTPException(status_code=404, detail="Persona history not found")

    return {"message": "Persona history deleted successfully"}
