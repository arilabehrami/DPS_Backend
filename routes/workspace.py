from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse
from services.workspace import (
    create_workspace,
    get_workspaces,
    get_workspace_by_id,
    update_workspace,
    delete_workspace
)

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.post("/", response_model=WorkspaceResponse)
def create_workspace_endpoint(data: WorkspaceCreate, db: Session = Depends(get_db)):
    return create_workspace(db, data)


@router.get("/", response_model=list[WorkspaceResponse])
def get_workspaces_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_workspaces(db, skip, limit)


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace_endpoint(workspace_id: int, db: Session = Depends(get_db)):
    workspace = get_workspace_by_id(db, workspace_id)

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return workspace


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
def update_workspace_endpoint(workspace_id: int, data: WorkspaceUpdate, db: Session = Depends(get_db)):
    workspace = update_workspace(db, workspace_id, data)

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return workspace


@router.delete("/{workspace_id}")
def delete_workspace_endpoint(workspace_id: int, db: Session = Depends(get_db)):
    workspace = delete_workspace(db, workspace_id)

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return {"message": "Workspace deleted successfully"}