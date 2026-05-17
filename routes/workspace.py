from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.workspace import Workspace
from schemas.workspace import WorkspaceCreate, WorkspaceResponse

router = APIRouter(
    prefix="/workspaces",
    tags=["Workspaces"]
)


@router.post("/", response_model=WorkspaceResponse)
def create_workspace(
    workspace_data: WorkspaceCreate,
    db: Session = Depends(get_db)
):
    workspace = Workspace(**workspace_data.model_dump())

    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    return workspace


@router.get("/", response_model=list[WorkspaceResponse])
def get_workspaces(db: Session = Depends(get_db)):
    return db.query(Workspace).all()


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(workspace_id: int, db: Session = Depends(get_db)):
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id
    ).first()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    return workspace