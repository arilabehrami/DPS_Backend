from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.settings import Settings
from models.user import User
from security.auth_security import get_current_user
from security.tenant import ensure_settings_access, ensure_user_access
from schemas.settings import SettingsCreate, SettingsUpdate, SettingsResponse
from services.settings import (
    create_settings,
    get_all_settings,
    get_settings_by_id,
    get_settings_by_user_id,
    update_settings,
    delete_settings
)

router = APIRouter(
    prefix="/settings",
    tags=["Settings"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=SettingsResponse)
def create_settings_endpoint(
    data: SettingsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.user_id is not None:
        ensure_user_access(db, data.user_id, current_user)
    return create_settings(db, data)


@router.get("/", response_model=list[SettingsResponse])
def get_all_settings_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Settings)
        .join(User, Settings.user_id == User.id)
        .filter(User.workspace_id == current_user.workspace_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{settings_id}", response_model=SettingsResponse)
def get_settings_endpoint(
    settings_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ensure_settings_access(db, settings_id, current_user)


@router.get("/user/{user_id}", response_model=SettingsResponse)
def get_settings_by_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_user_access(db, user_id, current_user)
    settings = get_settings_by_user_id(db, user_id)

    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    return settings


@router.put("/{settings_id}", response_model=SettingsResponse)
def update_settings_endpoint(
    settings_id: int,
    data: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_settings_access(db, settings_id, current_user)
    settings = update_settings(db, settings_id, data)

    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    return settings


@router.delete("/{settings_id}")
def delete_settings_endpoint(
    settings_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_settings_access(db, settings_id, current_user)
    settings = delete_settings(db, settings_id)

    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    return {"message": "Settings deleted successfully"}
