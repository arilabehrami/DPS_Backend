from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.role import Role
from schemas.role import RoleCreate, RoleResponse

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)


@router.post("/", response_model=RoleResponse)
def create_role(role_data: RoleCreate, db: Session = Depends(get_db)):
    role = Role(**role_data.model_dump())

    db.add(role)
    db.commit()
    db.refresh(role)

    return role


@router.get("/", response_model=list[RoleResponse])
def get_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()