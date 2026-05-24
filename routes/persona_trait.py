from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas.persona_trait import PersonaTraitCreate, PersonaTraitUpdate, PersonaTraitResponse
from services.persona_trait import (
    create_persona_trait,
    get_persona_trait_by_id,
    get_persona_traits,
    update_persona_trait,
    delete_persona_trait,
)
from routes.dependencies import require_roles

router = APIRouter(
    prefix="/persona-traits",
    tags=["Persona Traits"],
)


@router.post("/", response_model=PersonaTraitResponse)
def create_persona_trait_endpoint(
    data: PersonaTraitCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    return create_persona_trait(db, data)


@router.get("/", response_model=list[PersonaTraitResponse])
def list_persona_traits_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return get_persona_traits(db, skip=skip, limit=limit)


@router.get("/{persona_trait_id}", response_model=PersonaTraitResponse)
def get_persona_trait_endpoint(
    persona_trait_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_persona_trait_by_id(db, persona_trait_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="PersonaTrait not found")
    return db_obj


@router.put("/{persona_trait_id}", response_model=PersonaTraitResponse)
def update_persona_trait_endpoint(
    persona_trait_id: int,
    data: PersonaTraitUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = update_persona_trait(db, persona_trait_id, data)
    if not db_obj:
        raise HTTPException(status_code=404, detail="PersonaTrait not found")
    return db_obj


@router.delete("/{persona_trait_id}")
def delete_persona_trait_endpoint(
    persona_trait_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    deleted = delete_persona_trait(db, persona_trait_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="PersonaTrait not found")
    return {"message": "PersonaTrait deleted successfully"}
