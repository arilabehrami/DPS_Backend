from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.role import RoleCreate, RoleUpdate, RoleResponse
from services.role import (
    create_role,
    get_roles,
    get_role_by_id,
    update_role,
    delete_role
)

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post("/", response_model=RoleResponse)
def create_role_endpoint(data: RoleCreate, db: Session = Depends(get_db)):
    return create_role(db, data)


@router.get("/", response_model=list[RoleResponse])
def get_roles_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_roles(db, skip, limit)


@router.get("/{role_id}", response_model=RoleResponse)
def get_role_endpoint(role_id: int, db: Session = Depends(get_db)):
    role = get_role_by_id(db, role_id)

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    return role


@router.put("/{role_id}", response_model=RoleResponse)
def update_role_endpoint(role_id: int, data: RoleUpdate, db: Session = Depends(get_db)):
    role = update_role(db, role_id, data)

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    return role


@router.delete("/{role_id}")
def delete_role_endpoint(role_id: int, db: Session = Depends(get_db)):
    role = delete_role(db, role_id)

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    return {"message": "Role deleted successfully"}