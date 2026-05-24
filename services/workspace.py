from sqlalchemy.orm import Session
from models.workspace import Workspace
from schemas.workspace import WorkspaceCreate, WorkspaceUpdate


def create_workspace(db: Session, data: WorkspaceCreate) -> Workspace:
    db_obj = Workspace(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_workspace_by_id(db: Session, workspace_id: int) -> Workspace | None:
    return db.query(Workspace).filter(Workspace.id == workspace_id).first()


def get_workspaces(db: Session, skip: int = 0, limit: int = 100) -> list[Workspace]:
    return db.query(Workspace).offset(skip).limit(limit).all()


def update_workspace(db: Session, workspace_id: int, data: WorkspaceUpdate) -> Workspace | None:
    db_obj = get_workspace_by_id(db, workspace_id)
    if not db_obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_workspace(db: Session, workspace_id: int) -> bool:
    db_obj = get_workspace_by_id(db, workspace_id)
    if not db_obj:
        return False

    db.delete(db_obj)
    db.commit()
    return True
