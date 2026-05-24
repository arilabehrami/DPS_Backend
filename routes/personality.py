from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas.personality import PersonalityCreate, PersonalityUpdate, PersonalityResponse
from services.personality import (
    create_personality,
    get_personality_by_id,
    get_personalitys,
    update_personality,
    delete_personality,
)
from routes.dependencies import require_roles

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
    return create_personality(db, data)


@router.get("/", response_model=list[PersonalityResponse])
def list_personalitys_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return get_personalitys(db, skip=skip, limit=limit)


@router.get("/{personality_id}", response_model=PersonalityResponse)
def get_personality_endpoint(
    personality_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_personality_by_id(db, personality_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Personality not found")
    return db_obj


@router.put("/{personality_id}", response_model=PersonalityResponse)
def update_personality_endpoint(
    personality_id: int,
    data: PersonalityUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = update_personality(db, personality_id, data)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Personality not found")
    return db_obj


@router.delete("/{personality_id}")
def delete_personality_endpoint(
    personality_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    deleted = delete_personality(db, personality_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Personality not found")
    return {"message": "Personality deleted successfully"}
