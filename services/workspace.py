from sqlalchemy.orm import Session
from models.workspace import Workspace
from schemas.workspace import WorkspaceCreate, WorkspaceUpdate


def create_workspace(db: Session, data: WorkspaceCreate):
    workspace = Workspace(**data.dict(exclude_unset=True))
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace


def get_workspaces(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Workspace).offset(skip).limit(limit).all()


def get_workspace_by_id(db: Session, workspace_id: int):
    return db.query(Workspace).filter(Workspace.id == workspace_id).first()


def update_workspace(db: Session, workspace_id: int, data: WorkspaceUpdate):
    workspace = get_workspace_by_id(db, workspace_id)

    if not workspace:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(workspace, field, value)

    db.commit()
    db.refresh(workspace)
    return workspace


def delete_workspace(db: Session, workspace_id: int):
    workspace = get_workspace_by_id(db, workspace_id)

    if not workspace:
        return None

    db.delete(workspace)
    db.commit()
    return workspace