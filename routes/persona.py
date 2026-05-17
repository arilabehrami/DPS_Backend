from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.persona import PersonaCreate, PersonaUpdate, PersonaResponse
from services.persona import (
    create_persona,
    get_personas,
    get_persona_by_id,
    get_personas_by_user_id,
    get_personas_by_workspace_id,
    update_persona,
    delete_persona
)

router = APIRouter(prefix="/personas", tags=["Personas"])


@router.post("/", response_model=PersonaResponse)
def create_persona_endpoint(data: PersonaCreate, db: Session = Depends(get_db)):
    return create_persona(db, data)


@router.get("/", response_model=list[PersonaResponse])
def get_personas_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_personas(db, skip, limit)


@router.get("/{persona_id}", response_model=PersonaResponse)
def get_persona_endpoint(persona_id: int, db: Session = Depends(get_db)):
    persona = get_persona_by_id(db, persona_id)

    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    return persona


@router.get("/user/{user_id}", response_model=list[PersonaResponse])
def get_personas_by_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    return get_personas_by_user_id(db, user_id)


@router.get("/workspace/{workspace_id}", response_model=list[PersonaResponse])
def get_personas_by_workspace_endpoint(workspace_id: int, db: Session = Depends(get_db)):
    return get_personas_by_workspace_id(db, workspace_id)


@router.put("/{persona_id}", response_model=PersonaResponse)
def update_persona_endpoint(persona_id: int, data: PersonaUpdate, db: Session = Depends(get_db)):
    persona = update_persona(db, persona_id, data)

    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    return persona


@router.delete("/{persona_id}")
def delete_persona_endpoint(persona_id: int, db: Session = Depends(get_db)):
    persona = delete_persona(db, persona_id)

    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    return {"message": "Persona deleted successfully"}