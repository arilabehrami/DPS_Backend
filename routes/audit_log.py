from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.audit_log import AuditLog
from schemas.audit_log import AuditLogCreate, AuditLogUpdate, AuditLogResponse
from services.audit_log import (
    create_audit_log,
    get_audit_log_by_id,
    get_audit_logs,
    update_audit_log,
    delete_audit_log,
)
from routes.dependencies import require_roles
from security.tenant import ensure_user_access, ensure_workspace_access

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


@router.post("/", response_model=AuditLogResponse)
def create_audit_log_endpoint(
    data: AuditLogCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    if data.workspace_id is not None:
        ensure_workspace_access(data.workspace_id, current_user)
    ensure_user_access(db, data.user_id, current_user)
    return create_audit_log(db, data)


@router.get("/", response_model=list[AuditLogResponse])
def list_audit_logs_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return db.query(AuditLog).filter(AuditLog.workspace_id == current_user.workspace_id).offset(skip).limit(limit).all()


@router.get("/{audit_log_id}", response_model=AuditLogResponse)
def get_audit_log_endpoint(
    audit_log_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_audit_log_by_id(db, audit_log_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="AuditLog not found")
    return db_obj


@router.put("/{audit_log_id}", response_model=AuditLogResponse)
def update_audit_log_endpoint(
    audit_log_id: int,
    data: AuditLogUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = get_audit_log_by_id(db, audit_log_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="AuditLog not found")
    if data.workspace_id is not None:
        ensure_workspace_access(data.workspace_id, current_user)
    if data.user_id is not None:
        ensure_user_access(db, data.user_id, current_user)
    db_obj = update_audit_log(db, audit_log_id, data)
    return db_obj


@router.delete("/{audit_log_id}")
def delete_audit_log_endpoint(
    audit_log_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = get_audit_log_by_id(db, audit_log_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="AuditLog not found")
    deleted = delete_audit_log(db, audit_log_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="AuditLog not found")
    return {"message": "AuditLog deleted successfully"}
