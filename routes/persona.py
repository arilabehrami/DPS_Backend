from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from database import get_db
from models.persona import Persona
from schemas.persona import PersonaCreate, PersonaUpdate, PersonaResponse
from services.persona import create_persona, get_persona_by_id, update_persona, delete_persona
from routes.dependencies import normalize_role_name, require_roles
from security.tenant import ensure_workspace_access

router = APIRouter(prefix="/personas", tags=["Personas"])


@router.post("/", response_model=PersonaResponse)
def create_persona_endpoint(
    data: PersonaCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    is_admin = normalize_role_name(current_user.role.name if current_user.role else None) == "admin"
    ensure_workspace_access(data.workspace_id, current_user)
    if not is_admin:
        data.user_id = current_user.id
    elif data.user_id is None:
        data.user_id = current_user.id
    return create_persona(db, data)


@router.get("/", response_model=list[PersonaResponse])
def list_personas_endpoint(
    search: str | None = None,
    workspace_id: int | None = None,
    user_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    query = db.query(Persona).filter(Persona.workspace_id == current_user.workspace_id)

    if search:
        like_value = f"%{search}%"
        query = query.filter(or_(Persona.name.ilike(like_value), Persona.description.ilike(like_value)))
    if workspace_id is not None:
        ensure_workspace_access(workspace_id, current_user)
        query = query.filter(Persona.workspace_id == workspace_id)
    if user_id is not None:
        query = query.filter(Persona.user_id == user_id)

    return query.offset(skip).limit(limit).all()


@router.get("/{persona_id}", response_model=PersonaResponse)
def get_persona_endpoint(
    persona_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_persona_by_id(db, persona_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="Persona not found")
    return db_obj


@router.put("/{persona_id}", response_model=PersonaResponse)
def update_persona_endpoint(
    persona_id: int,
    data: PersonaUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    is_admin = normalize_role_name(current_user.role.name if current_user.role else None) == "admin"
    db_obj = get_persona_by_id(db, persona_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="Persona not found")
    if not is_admin and db_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only manage your own personas")
    if data.workspace_id is not None:
        ensure_workspace_access(data.workspace_id, current_user)
    if not is_admin:
        if data.user_id is not None and data.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can only manage your own personas")
        data.user_id = current_user.id
    db_obj = update_persona(db, persona_id, data)
    return db_obj


@router.delete("/{persona_id}")
def delete_persona_endpoint(
    persona_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    is_admin = normalize_role_name(current_user.role.name if current_user.role else None) == "admin"
    db_obj = get_persona_by_id(db, persona_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="Persona not found")
    if not is_admin and db_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only manage your own personas")
    deleted = delete_persona(db, persona_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Persona not found")
    return {"message": "Persona deleted successfully"}
