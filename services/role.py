from sqlalchemy.orm import Session
from models.role import Role
from schemas.role import RoleCreate, RoleUpdate


def create_role(db: Session, data: RoleCreate):
    role = Role(**data.dict(exclude_unset=True))
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def get_roles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Role).offset(skip).limit(limit).all()


def get_role_by_id(db: Session, role_id: int):
    return db.query(Role).filter(Role.id == role_id).first()


def update_role(db: Session, role_id: int, data: RoleUpdate):
    role = get_role_by_id(db, role_id)

    if not role:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(role, field, value)

    db.commit()
    db.refresh(role)
    return role


def delete_role(db: Session, role_id: int):
    role = get_role_by_id(db, role_id)

    if not role:
        return None

    db.delete(role)
    db.commit()
    return role