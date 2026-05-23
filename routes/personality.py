from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.personality import Personality
from models.user import User
from security.auth_security import get_current_user
from security.tenant import ensure_user_access, ensure_workspace_access
from schemas.personality import PersonalityCreate, PersonalityUpdate, PersonalityResponse
from services.cache_service import get_or_set_list_cache, invalidate_cache_prefix
from services.personality import (
    create_personality,
    get_personalities,
    get_personality_by_id,
    get_personalities_by_user_id,
    get_personalities_by_workspace_id,
    search_personalities,
    update_personality,
    delete_personality
)

router = APIRouter(
    prefix="/personalities",
    tags=["Personalities"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=PersonalityResponse)
def create_personality_endpoint(
    data: PersonalityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_workspace_access(data.workspace_id, current_user)
    if data.user_id is not None:
        ensure_user_access(db, data.user_id, current_user)
    personality = create_personality(db, data)
    invalidate_cache_prefix("personalities:")
    return personality


@router.get("/", response_model=list[PersonalityResponse])
def get_personalities_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_or_set_list_cache(
        f"personalities:workspace:{current_user.workspace_id}:list:skip={skip}:limit={limit}",
        lambda: db.query(Personality)
        .filter(Personality.workspace_id == current_user.workspace_id)
        .offset(skip)
        .limit(limit)
        .all(),
        PersonalityResponse,
    )


@router.get("/search", response_model=list[PersonalityResponse])
def search_personalities_endpoint(
    keyword: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_or_set_list_cache(
        f"personalities:workspace:{current_user.workspace_id}:search:keyword={keyword}",
        lambda: db.query(Personality)
        .filter(Personality.workspace_id == current_user.workspace_id)
        .filter(Personality.name.ilike(f"%{keyword}%"))
        .all(),
        PersonalityResponse,
    )


@router.get("/{personality_id}", response_model=PersonalityResponse)
def get_personality_endpoint(
    personality_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    personality = (
        db.query(Personality)
        .filter(Personality.id == personality_id)
        .filter(Personality.workspace_id == current_user.workspace_id)
        .first()
    )

    if not personality:
        raise HTTPException(status_code=404, detail="Personality not found")

    return personality


@router.get("/user/{user_id}", response_model=list[PersonalityResponse])
def get_personalities_by_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_user_access(db, user_id, current_user)
    return (
        db.query(Personality)
        .filter(Personality.user_id == user_id)
        .filter(Personality.workspace_id == current_user.workspace_id)
        .all()
    )


@router.get("/workspace/{workspace_id}", response_model=list[PersonalityResponse])
def get_personalities_by_workspace_endpoint(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_workspace_access(workspace_id, current_user)
    return get_personalities_by_workspace_id(db, workspace_id)


@router.put("/{personality_id}", response_model=PersonalityResponse)
def update_personality_endpoint(
    personality_id: int,
    data: PersonalityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    personality = get_personality_by_id(db, personality_id)
    if not personality:
        raise HTTPException(status_code=404, detail="Personality not found")

    ensure_workspace_access(personality.workspace_id, current_user)
    personality = update_personality(db, personality_id, data)

    if not personality:
        raise HTTPException(status_code=404, detail="Personality not found")

    invalidate_cache_prefix("personalities:")
    return personality


@router.delete("/{personality_id}")
def delete_personality_endpoint(
    personality_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    personality = get_personality_by_id(db, personality_id)
    if not personality:
        raise HTTPException(status_code=404, detail="Personality not found")

    ensure_workspace_access(personality.workspace_id, current_user)
    personality = delete_personality(db, personality_id)

    if not personality:
        raise HTTPException(status_code=404, detail="Personality not found")

    invalidate_cache_prefix("personalities:")
    return {"message": "Personality deleted successfully"}
