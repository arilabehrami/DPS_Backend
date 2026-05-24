from sqlalchemy.orm import Session
from models.role import Role
from schemas.role import RoleCreate, RoleUpdate


def create_role(db: Session, data: RoleCreate) -> Role:
    db_obj = Role(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_role_by_id(db: Session, role_id: int) -> Role | None:
    return db.query(Role).filter(Role.id == role_id).first()


def get_roles(db: Session, skip: int = 0, limit: int = 100) -> list[Role]:
    return db.query(Role).offset(skip).limit(limit).all()


def update_role(db: Session, role_id: int, data: RoleUpdate) -> Role | None:
    db_obj = get_role_by_id(db, role_id)
    if not db_obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_role(db: Session, role_id: int) -> bool:
    db_obj = get_role_by_id(db, role_id)
    if not db_obj:
        return False

    db.delete(db_obj)
    db.commit()
    return True
