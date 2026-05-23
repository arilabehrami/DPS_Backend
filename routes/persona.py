from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.persona import Persona
from models.user import User
from security.auth_security import get_current_user
from security.tenant import ensure_user_access, ensure_workspace_access
from schemas.persona import PersonaCreate, PersonaUpdate, PersonaResponse
from services.cache_service import get_or_set_list_cache, invalidate_cache_prefix
from services.persona import (
    create_persona,
    get_personas,
    get_persona_by_id,
    get_personas_by_user_id,
    get_personas_by_workspace_id,
    update_persona,
    delete_persona
)

router = APIRouter(
    prefix="/personas",
    tags=["Personas"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=PersonaResponse)
def create_persona_endpoint(
    data: PersonaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_workspace_access(data.workspace_id, current_user)
    ensure_user_access(db, data.user_id, current_user)
    persona = create_persona(db, data)
    invalidate_cache_prefix("personas:")
    return persona


@router.get("/", response_model=list[PersonaResponse])
def get_personas_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_or_set_list_cache(
        f"personas:workspace:{current_user.workspace_id}:list:skip={skip}:limit={limit}",
        lambda: db.query(Persona)
        .filter(Persona.workspace_id == current_user.workspace_id)
        .offset(skip)
        .limit(limit)
        .all(),
        PersonaResponse,
    )


@router.get("/{persona_id}", response_model=PersonaResponse)
def get_persona_endpoint(
    persona_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    persona = (
        db.query(Persona)
        .filter(Persona.id == persona_id)
        .filter(Persona.workspace_id == current_user.workspace_id)
        .first()
    )

    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    return persona


@router.get("/user/{user_id}", response_model=list[PersonaResponse])
def get_personas_by_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_user_access(db, user_id, current_user)
    return get_or_set_list_cache(
        f"personas:workspace:{current_user.workspace_id}:user:{user_id}",
        lambda: db.query(Persona)
        .filter(Persona.user_id == user_id)
        .filter(Persona.workspace_id == current_user.workspace_id)
        .all(),
        PersonaResponse,
    )


@router.get("/workspace/{workspace_id}", response_model=list[PersonaResponse])
def get_personas_by_workspace_endpoint(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_workspace_access(workspace_id, current_user)
    return get_or_set_list_cache(
        f"personas:workspace:{current_user.workspace_id}",
        lambda: get_personas_by_workspace_id(db, workspace_id),
        PersonaResponse,
    )


@router.put("/{persona_id}", response_model=PersonaResponse)
def update_persona_endpoint(
    persona_id: int,
    data: PersonaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    persona = get_persona_by_id(db, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    ensure_workspace_access(persona.workspace_id, current_user)
    persona = update_persona(db, persona_id, data)

    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    invalidate_cache_prefix("personas:")
    return persona


@router.delete("/{persona_id}")
def delete_persona_endpoint(
    persona_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    persona = get_persona_by_id(db, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    ensure_workspace_access(persona.workspace_id, current_user)
    persona = delete_persona(db, persona_id)

    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    invalidate_cache_prefix("personas:")
    return {"message": "Persona deleted successfully"}
