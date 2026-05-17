from sqlalchemy.orm import Session
from models.audit_log import AuditLog
from schemas.audit_log import AuditLogCreate, AuditLogUpdate


def create_audit_log(db: Session, data: AuditLogCreate):
    audit_log = AuditLog(**data.dict(exclude_unset=True))
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log


def get_audit_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(AuditLog).offset(skip).limit(limit).all()


def get_audit_log_by_id(db: Session, audit_log_id: int):
    return db.query(AuditLog).filter(AuditLog.id == audit_log_id).first()


def get_audit_logs_by_action(db: Session, action: str):
    return db.query(AuditLog).filter(AuditLog.action == action).all()


def update_audit_log(db: Session, audit_log_id: int, data: AuditLogUpdate):
    audit_log = get_audit_log_by_id(db, audit_log_id)

    if not audit_log:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(audit_log, field, value)

    db.commit()
    db.refresh(audit_log)
    return audit_log


def delete_audit_log(db: Session, audit_log_id: int):
    audit_log = get_audit_log_by_id(db, audit_log_id)

    if not audit_log:
        return None

    db.delete(audit_log)
    db.commit()
    return audit_log