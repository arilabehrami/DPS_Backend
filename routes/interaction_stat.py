from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.interaction_stat import InteractionStat
from schemas.interaction_stat import InteractionStatCreate, InteractionStatUpdate, InteractionStatResponse
from services.interaction_stat import (
    create_interaction_stat,
    get_interaction_stat_by_id,
    get_interaction_stats,
    update_interaction_stat,
    delete_interaction_stat,
)
from routes.dependencies import require_roles
from security.tenant import ensure_conversation_access, ensure_personality_access, ensure_user_access, ensure_workspace_access

router = APIRouter(
    prefix="/interaction-stats",
    tags=["Interaction Stats"],
)


@router.post("/", response_model=InteractionStatResponse)
def create_interaction_stat_endpoint(
    data: InteractionStatCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    ensure_workspace_access(data.workspace_id, current_user)
    ensure_user_access(db, data.user_id, current_user)
    ensure_personality_access(db, data.personality_id, current_user)
    if data.conversation_id is not None:
        ensure_conversation_access(db, data.conversation_id, current_user)
    return create_interaction_stat(db, data)


@router.get("/", response_model=list[InteractionStatResponse])
def list_interaction_stats_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return db.query(InteractionStat).filter(InteractionStat.workspace_id == current_user.workspace_id).offset(skip).limit(limit).all()


@router.get("/{interaction_stat_id}", response_model=InteractionStatResponse)
def get_interaction_stat_endpoint(
    interaction_stat_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_interaction_stat_by_id(db, interaction_stat_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="InteractionStat not found")
    return db_obj


@router.put("/{interaction_stat_id}", response_model=InteractionStatResponse)
def update_interaction_stat_endpoint(
    interaction_stat_id: int,
    data: InteractionStatUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = get_interaction_stat_by_id(db, interaction_stat_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="InteractionStat not found")
    if data.workspace_id is not None:
        ensure_workspace_access(data.workspace_id, current_user)
    if data.user_id is not None:
        ensure_user_access(db, data.user_id, current_user)
    if data.personality_id is not None:
        ensure_personality_access(db, data.personality_id, current_user)
    if data.conversation_id is not None:
        ensure_conversation_access(db, data.conversation_id, current_user)
    db_obj = update_interaction_stat(db, interaction_stat_id, data)
    return db_obj


@router.delete("/{interaction_stat_id}")
def delete_interaction_stat_endpoint(
    interaction_stat_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = get_interaction_stat_by_id(db, interaction_stat_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="InteractionStat not found")
    deleted = delete_interaction_stat(db, interaction_stat_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="InteractionStat not found")
    return {"message": "InteractionStat deleted successfully"}
