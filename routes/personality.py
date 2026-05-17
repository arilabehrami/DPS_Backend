from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.personality import Personality
from schemas.personality import (
    PersonalityCreate,
    PersonalityResponse
)

router = APIRouter(
    prefix="/personalities",
    tags=["Personalities"]
)


@router.post("/", response_model=PersonalityResponse)
def create_personality(
    personality_data: PersonalityCreate,
    db: Session = Depends(get_db)
):
    personality = Personality(**personality_data.model_dump())

    db.add(personality)
    db.commit()
    db.refresh(personality)

    return personality


@router.get("/", response_model=list[PersonalityResponse])
def get_personalities(db: Session = Depends(get_db)):
    return db.query(Personality).all()


@router.get("/{personality_id}", response_model=PersonalityResponse)
def get_personality(personality_id: int, db: Session = Depends(get_db)):
    personality = db.query(Personality).filter(
        Personality.id == personality_id
    ).first()

    if not personality:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personality not found"
        )

    return personality


@router.delete("/{personality_id}")
def delete_personality(personality_id: int, db: Session = Depends(get_db)):
    personality = db.query(Personality).filter(
        Personality.id == personality_id
    ).first()

    if not personality:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personality not found"
        )

    db.delete(personality)
    db.commit()

    return {
        "message": "Personality deleted"
    }
    
@router.get("/search/")
def search_personality(
    name: str,
    db: Session = Depends(get_db)
):
    return db.query(Personality).filter(
        Personality.name.ilike(f"%{name}%")
    ).all()