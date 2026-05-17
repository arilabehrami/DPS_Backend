from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.personality import PersonalityCreate, PersonalityUpdate, PersonalityResponse
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

router = APIRouter(prefix="/personalities", tags=["Personalities"])


@router.post("/", response_model=PersonalityResponse)
def create_personality_endpoint(data: PersonalityCreate, db: Session = Depends(get_db)):
    return create_personality(db, data)


@router.get("/", response_model=list[PersonalityResponse])
def get_personalities_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_personalities(db, skip, limit)


@router.get("/search", response_model=list[PersonalityResponse])
def search_personalities_endpoint(keyword: str, db: Session = Depends(get_db)):
    return search_personalities(db, keyword)


@router.get("/{personality_id}", response_model=PersonalityResponse)
def get_personality_endpoint(personality_id: int, db: Session = Depends(get_db)):
    personality = get_personality_by_id(db, personality_id)

    if not personality:
        raise HTTPException(status_code=404, detail="Personality not found")

    return personality


@router.get("/user/{user_id}", response_model=list[PersonalityResponse])
def get_personalities_by_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    return get_personalities_by_user_id(db, user_id)


@router.get("/workspace/{workspace_id}", response_model=list[PersonalityResponse])
def get_personalities_by_workspace_endpoint(workspace_id: int, db: Session = Depends(get_db)):
    return get_personalities_by_workspace_id(db, workspace_id)


@router.put("/{personality_id}", response_model=PersonalityResponse)
def update_personality_endpoint(personality_id: int, data: PersonalityUpdate, db: Session = Depends(get_db)):
    personality = update_personality(db, personality_id, data)

    if not personality:
        raise HTTPException(status_code=404, detail="Personality not found")

    return personality


@router.delete("/{personality_id}")
def delete_personality_endpoint(personality_id: int, db: Session = Depends(get_db)):
    personality = delete_personality(db, personality_id)

    if not personality:
        raise HTTPException(status_code=404, detail="Personality not found")

    return {"message": "Personality deleted successfully"}