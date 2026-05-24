from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.personality import Personality
from schemas.personality import PersonalityCreate, PersonalityUpdate, PersonalityResponse
from services.personality import (
    create_personality,
    get_personality_by_id,
    get_personalitys,
    update_personality,
    delete_personality,
)
from routes.dependencies import require_roles
from security.tenant import ensure_persona_access, ensure_user_access, ensure_workspace_access

router = APIRouter(
    prefix="/personalitys",
    tags=["Personalitys"],
)


@router.post("/", response_model=PersonalityResponse)
def create_personality_endpoint(
    data: PersonalityCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    ensure_workspace_access(data.workspace_id, current_user)
    ensure_persona_access(db, data.persona_id, current_user)
    if data.user_id is not None:
        ensure_user_access(db, data.user_id, current_user)
    return create_personality(db, data)


@router.get("/", response_model=list[PersonalityResponse])
def list_personalitys_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return (
        db.query(Personality)
        .filter(Personality.workspace_id == current_user.workspace_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{personality_id}", response_model=PersonalityResponse)
def get_personality_endpoint(
    personality_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_personality_by_id(db, personality_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="Personality not found")
    return db_obj


@router.put("/{personality_id}", response_model=PersonalityResponse)
def update_personality_endpoint(
    personality_id: int,
    data: PersonalityUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = get_personality_by_id(db, personality_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="Personality not found")
    if data.workspace_id is not None:
        ensure_workspace_access(data.workspace_id, current_user)
    if data.persona_id is not None:
        ensure_persona_access(db, data.persona_id, current_user)
    if data.user_id is not None:
        ensure_user_access(db, data.user_id, current_user)
    db_obj = update_personality(db, personality_id, data)
    return db_obj


@router.delete("/{personality_id}")
def delete_personality_endpoint(
    personality_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = get_personality_by_id(db, personality_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="Personality not found")
    deleted = delete_personality(db, personality_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Personality not found")
    return {"message": "Personality deleted successfully"}
