from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.audit_log import AuditLogCreate, AuditLogUpdate, AuditLogResponse
from services.audit_log import (
    create_audit_log,
    get_audit_logs,
    get_audit_log_by_id,
    get_audit_logs_by_action,
    update_audit_log,
    delete_audit_log
)

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.post("/", response_model=AuditLogResponse)
def create_audit_log_endpoint(data: AuditLogCreate, db: Session = Depends(get_db)):
    return create_audit_log(db, data)


@router.get("/", response_model=list[AuditLogResponse])
def get_audit_logs_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_audit_logs(db, skip, limit)


@router.get("/{audit_log_id}", response_model=AuditLogResponse)
def get_audit_log_endpoint(audit_log_id: int, db: Session = Depends(get_db)):
    audit_log = get_audit_log_by_id(db, audit_log_id)

    if not audit_log:
        raise HTTPException(status_code=404, detail="Audit log not found")

    return audit_log


@router.get("/action/{action}", response_model=list[AuditLogResponse])
def get_audit_logs_by_action_endpoint(action: str, db: Session = Depends(get_db)):
    return get_audit_logs_by_action(db, action)


@router.put("/{audit_log_id}", response_model=AuditLogResponse)
def update_audit_log_endpoint(audit_log_id: int, data: AuditLogUpdate, db: Session = Depends(get_db)):
    audit_log = update_audit_log(db, audit_log_id, data)

    if not audit_log:
        raise HTTPException(status_code=404, detail="Audit log not found")

    return audit_log


@router.delete("/{audit_log_id}")
def delete_audit_log_endpoint(audit_log_id: int, db: Session = Depends(get_db)):
    audit_log = delete_audit_log(db, audit_log_id)

    if not audit_log:
        raise HTTPException(status_code=404, detail="Audit log not found")

    return {"message": "Audit log deleted successfully"}