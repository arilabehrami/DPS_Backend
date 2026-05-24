from sqlalchemy.orm import Session
from models.audit_log import AuditLog
from schemas.audit_log import AuditLogCreate, AuditLogUpdate


def create_audit_log(db: Session, data: AuditLogCreate) -> AuditLog:
    db_obj = AuditLog(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_audit_log_by_id(db: Session, audit_log_id: int) -> AuditLog | None:
    return db.query(AuditLog).filter(AuditLog.id == audit_log_id).first()


def get_audit_logs(db: Session, skip: int = 0, limit: int = 100) -> list[AuditLog]:
    return db.query(AuditLog).offset(skip).limit(limit).all()


def update_audit_log(db: Session, audit_log_id: int, data: AuditLogUpdate) -> AuditLog | None:
    db_obj = get_audit_log_by_id(db, audit_log_id)
    if not db_obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_audit_log(db: Session, audit_log_id: int) -> bool:
    db_obj = get_audit_log_by_id(db, audit_log_id)
    if not db_obj:
        return False

    db.delete(db_obj)
    db.commit()
    return True
