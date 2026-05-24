from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas.audit_log import AuditLogCreate, AuditLogUpdate, AuditLogResponse
from services.audit_log import (
    create_audit_log,
    get_audit_log_by_id,
    get_audit_logs,
    update_audit_log,
    delete_audit_log,
)
from routes.dependencies import require_roles

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
    return create_audit_log(db, data)


@router.get("/", response_model=list[AuditLogResponse])
def list_audit_logs_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return get_audit_logs(db, skip=skip, limit=limit)


@router.get("/{audit_log_id}", response_model=AuditLogResponse)
def get_audit_log_endpoint(
    audit_log_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_audit_log_by_id(db, audit_log_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="AuditLog not found")
    return db_obj


@router.put("/{audit_log_id}", response_model=AuditLogResponse)
def update_audit_log_endpoint(
    audit_log_id: int,
    data: AuditLogUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = update_audit_log(db, audit_log_id, data)
    if not db_obj:
        raise HTTPException(status_code=404, detail="AuditLog not found")
    return db_obj


@router.delete("/{audit_log_id}")
def delete_audit_log_endpoint(
    audit_log_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    deleted = delete_audit_log(db, audit_log_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="AuditLog not found")
    return {"message": "AuditLog deleted successfully"}
