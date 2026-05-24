from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas.role import RoleCreate, RoleUpdate, RoleResponse
from services.role import (
    create_role,
    get_role_by_id,
    get_roles,
    update_role,
    delete_role,
)
from routes.dependencies import require_roles

router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
)


@router.post("/", response_model=RoleResponse)
def create_role_endpoint(
    data: RoleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    return create_role(db, data)


@router.get("/", response_model=list[RoleResponse])
def list_roles_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    return get_roles(db, skip=skip, limit=limit)


@router.get("/{role_id}", response_model=RoleResponse)
def get_role_endpoint(
    role_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = get_role_by_id(db, role_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_obj


@router.put("/{role_id}", response_model=RoleResponse)
def update_role_endpoint(
    role_id: int,
    data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = update_role(db, role_id, data)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_obj


@router.delete("/{role_id}")
def delete_role_endpoint(
    role_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    deleted = delete_role(db, role_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Role deleted successfully"}
