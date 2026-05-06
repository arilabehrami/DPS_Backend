from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.personality import Personality
from schemas.personality import PersonalityCreate, PersonalityUpdate, PersonalityOut

router = APIRouter(prefix="/personalities", tags=["Personality"])

@router.post("/", response_model=PersonalityOut)
def create_personality(personality: PersonalityCreate, db: Session = Depends(get_db)):
    new_p = Personality(**personality.dict())
    db.add(new_p)
    db.commit()
    db.refresh(new_p)
    return new_p

@router.get("/", response_model=list[PersonalityOut])
def get_all_personalities(db: Session = Depends(get_db)):
    return db.query(Personality).all()

@router.get("/{id}", response_model=PersonalityOut)
def get_personality(id: int, db: Session = Depends(get_db)):
    p = db.query(Personality).filter(Personality.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    return p

@router.put("/{id}", response_model=PersonalityOut)
def update_personality(id: int, personality: PersonalityUpdate, db: Session = Depends(get_db)):
    p = db.query(Personality).filter(Personality.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    for key, value in personality.dict(exclude_unset=True).items():
        setattr(p, key, value)
    db.commit()
    db.refresh(p)
    return p

@router.delete("/{id}")
def delete_personality(id: int, db: Session = Depends(get_db)):
    p = db.query(Personality).filter(Personality.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(p)
    db.commit()
    return {"message": "Deleted successfully"}
