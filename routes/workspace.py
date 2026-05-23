from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from security.auth_security import require_roles
from security.tenant import ensure_workspace_access
from models.user import User
from schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse
from services.workspace import (
    create_workspace,
    get_workspaces,
    get_workspace_by_id,
    update_workspace,
    delete_workspace
)

router = APIRouter(
    prefix="/workspaces",
    tags=["Workspaces"],
    dependencies=[Depends(require_roles("admin"))],
)


@router.post("/", response_model=WorkspaceResponse)
def create_workspace_endpoint(data: WorkspaceCreate, db: Session = Depends(get_db)):
    return create_workspace(db, data)


@router.get("/", response_model=list[WorkspaceResponse])
def get_workspaces_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    workspace = get_workspace_by_id(db, current_user.workspace_id)
    return [workspace] if workspace else []


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace_endpoint(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    ensure_workspace_access(workspace_id, current_user)
    workspace = get_workspace_by_id(db, workspace_id)

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return workspace


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
def update_workspace_endpoint(
    workspace_id: int,
    data: WorkspaceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    ensure_workspace_access(workspace_id, current_user)
    workspace = update_workspace(db, workspace_id, data)

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return workspace


@router.delete("/{workspace_id}")
def delete_workspace_endpoint(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    ensure_workspace_access(workspace_id, current_user)
    workspace = delete_workspace(db, workspace_id)

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return {"message": "Workspace deleted successfully"}
