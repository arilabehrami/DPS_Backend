from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.settings import SettingsCreate, SettingsUpdate, SettingsResponse
from services.settings import (
    create_settings,
    get_all_settings,
    get_settings_by_id,
    get_settings_by_user_id,
    update_settings,
    delete_settings
)

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.post("/", response_model=SettingsResponse)
def create_settings_endpoint(data: SettingsCreate, db: Session = Depends(get_db)):
    return create_settings(db, data)


@router.get("/", response_model=list[SettingsResponse])
def get_all_settings_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_all_settings(db, skip, limit)


@router.get("/{settings_id}", response_model=SettingsResponse)
def get_settings_endpoint(settings_id: int, db: Session = Depends(get_db)):
    settings = get_settings_by_id(db, settings_id)

    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    return settings


@router.get("/user/{user_id}", response_model=SettingsResponse)
def get_settings_by_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    settings = get_settings_by_user_id(db, user_id)

    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    return settings


@router.put("/{settings_id}", response_model=SettingsResponse)
def update_settings_endpoint(settings_id: int, data: SettingsUpdate, db: Session = Depends(get_db)):
    settings = update_settings(db, settings_id, data)

    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    return settings


@router.delete("/{settings_id}")
def delete_settings_endpoint(settings_id: int, db: Session = Depends(get_db)):
    settings = delete_settings(db, settings_id)

    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    return {"message": "Settings deleted successfully"}