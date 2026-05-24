from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse
from services.workspace import (
    create_workspace,
    get_workspace_by_id,
    get_workspaces,
    update_workspace,
    delete_workspace,
)
from routes.dependencies import require_roles

router = APIRouter(
    prefix="/workspaces",
    tags=["Workspaces"],
)


def is_admin(user) -> bool:
    return bool(user.role and user.role.name.lower() == "admin")


@router.post("/", response_model=WorkspaceResponse)
def create_workspace_endpoint(
    data: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    return create_workspace(db, data)


@router.get("/", response_model=list[WorkspaceResponse])
def list_workspaces_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    return get_workspaces(db, skip=skip, limit=limit)


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace_endpoint(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_workspace_by_id(db, workspace_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Workspace not found")
    if not is_admin(current_user) and workspace_id != current_user.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Users can only access their own workspace",
        )
    return db_obj


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
def update_workspace_endpoint(
    workspace_id: int,
    data: WorkspaceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = update_workspace(db, workspace_id, data)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return db_obj


@router.delete("/{workspace_id}")
def delete_workspace_endpoint(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    deleted = delete_workspace(db, workspace_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return {"message": "Workspace deleted successfully"}
