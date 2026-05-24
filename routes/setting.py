from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.setting import Setting
from schemas.setting import SettingCreate, SettingUpdate, SettingResponse
from services.setting import (
    create_setting,
    get_setting_by_id,
    get_settings,
    update_setting,
    delete_setting,
)
from routes.dependencies import require_roles
from security.tenant import ensure_setting_access, ensure_user_access, ensure_workspace_access

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
    if data.workspace_id is not None:
        ensure_workspace_access(data.workspace_id, current_user)
    if data.user_id is not None:
        ensure_user_access(db, data.user_id, current_user)
    return create_setting(db, data)


@router.get("/", response_model=list[SettingResponse])
def list_settings_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return (
        db.query(Setting)
        .filter(
            (Setting.workspace_id == current_user.workspace_id)
            | (Setting.user_id == current_user.id)
            | ((Setting.workspace_id.is_(None)) & (Setting.user_id.is_(None)))
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{setting_id}", response_model=SettingResponse)
def get_setting_endpoint(
    setting_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = ensure_setting_access(db, setting_id, current_user)
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
    db_obj = ensure_setting_access(db, setting_id, current_user)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Setting not found")
    if data.workspace_id is not None:
        ensure_workspace_access(data.workspace_id, current_user)
    if data.user_id is not None:
        ensure_user_access(db, data.user_id, current_user)
    db_obj = update_setting(db, setting_id, data)
    return db_obj


@router.delete("/{setting_id}")
def delete_setting_endpoint(
    setting_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    ensure_setting_access(db, setting_id, current_user)
    deleted = delete_setting(db, setting_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Setting not found")
    return {"message": "Setting deleted successfully"}
