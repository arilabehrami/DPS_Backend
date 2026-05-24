from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas.setting import SettingCreate, SettingUpdate, SettingResponse
from services.setting import (
    create_setting,
    get_setting_by_id,
    get_settings,
    update_setting,
    delete_setting,
)
from routes.dependencies import require_roles

router = APIRouter(
    prefix="/settings",
    tags=["Settings"],
)


@router.post("/", response_model=SettingResponse)
def create_setting_endpoint(
    data: SettingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    return create_setting(db, data)


@router.get("/", response_model=list[SettingResponse])
def list_settings_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return get_settings(db, skip=skip, limit=limit)


@router.get("/{setting_id}", response_model=SettingResponse)
def get_setting_endpoint(
    setting_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_setting_by_id(db, setting_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Setting not found")
    return db_obj


@router.put("/{setting_id}", response_model=SettingResponse)
def update_setting_endpoint(
    setting_id: int,
    data: SettingUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = update_setting(db, setting_id, data)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Setting not found")
    return db_obj


@router.delete("/{setting_id}")
def delete_setting_endpoint(
    setting_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    deleted = delete_setting(db, setting_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Setting not found")
    return {"message": "Setting deleted successfully"}
