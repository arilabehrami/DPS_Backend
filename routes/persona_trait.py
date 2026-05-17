from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.persona_trait import PersonaTraitCreate, PersonaTraitUpdate, PersonaTraitResponse
from services.persona_trait import (
    create_persona_trait,
    get_persona_traits,
    get_persona_trait_by_id,
    get_persona_traits_by_persona_id,
    update_persona_trait,
    delete_persona_trait
)

router = APIRouter(prefix="/persona-traits", tags=["Persona Traits"])


@router.post("/", response_model=PersonaTraitResponse)
def create_persona_trait_endpoint(data: PersonaTraitCreate, db: Session = Depends(get_db)):
    return create_persona_trait(db, data)


@router.get("/", response_model=list[PersonaTraitResponse])
def get_persona_traits_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_persona_traits(db, skip, limit)


@router.get("/{trait_id}", response_model=PersonaTraitResponse)
def get_persona_trait_endpoint(trait_id: int, db: Session = Depends(get_db)):
    persona_trait = get_persona_trait_by_id(db, trait_id)

    if not persona_trait:
        raise HTTPException(status_code=404, detail="Persona trait not found")

    return persona_trait


@router.get("/persona/{persona_id}", response_model=list[PersonaTraitResponse])
def get_persona_traits_by_persona_endpoint(persona_id: int, db: Session = Depends(get_db)):
    return get_persona_traits_by_persona_id(db, persona_id)


@router.put("/{trait_id}", response_model=PersonaTraitResponse)
def update_persona_trait_endpoint(trait_id: int, data: PersonaTraitUpdate, db: Session = Depends(get_db)):
    persona_trait = update_persona_trait(db, trait_id, data)

    if not persona_trait:
        raise HTTPException(status_code=404, detail="Persona trait not found")

    return persona_trait


@router.delete("/{trait_id}")
def delete_persona_trait_endpoint(trait_id: int, db: Session = Depends(get_db)):
    persona_trait = delete_persona_trait(db, trait_id)

    if not persona_trait:
        raise HTTPException(status_code=404, detail="Persona trait not found")

    return {"message": "Persona trait deleted successfully"}