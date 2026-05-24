from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas.persona_history import PersonaHistoryCreate, PersonaHistoryUpdate, PersonaHistoryResponse
from services.persona_history import (
    create_persona_history,
    get_persona_history_by_id,
    get_persona_historys,
    update_persona_history,
    delete_persona_history,
)
from routes.dependencies import require_roles

router = APIRouter(
    prefix="/persona-historys",
    tags=["Persona Historys"],
)


@router.post("/", response_model=PersonaHistoryResponse)
def create_persona_history_endpoint(
    data: PersonaHistoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    return create_persona_history(db, data)


@router.get("/", response_model=list[PersonaHistoryResponse])
def list_persona_historys_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return get_persona_historys(db, skip=skip, limit=limit)


@router.get("/{persona_history_id}", response_model=PersonaHistoryResponse)
def get_persona_history_endpoint(
    persona_history_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_persona_history_by_id(db, persona_history_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="PersonaHistory not found")
    return db_obj


@router.put("/{persona_history_id}", response_model=PersonaHistoryResponse)
def update_persona_history_endpoint(
    persona_history_id: int,
    data: PersonaHistoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = update_persona_history(db, persona_history_id, data)
    if not db_obj:
        raise HTTPException(status_code=404, detail="PersonaHistory not found")
    return db_obj


@router.delete("/{persona_history_id}")
def delete_persona_history_endpoint(
    persona_history_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    deleted = delete_persona_history(db, persona_history_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="PersonaHistory not found")
    return {"message": "PersonaHistory deleted successfully"}
