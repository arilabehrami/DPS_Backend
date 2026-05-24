from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas.interaction_stat import InteractionStatCreate, InteractionStatUpdate, InteractionStatResponse
from services.interaction_stat import (
    create_interaction_stat,
    get_interaction_stat_by_id,
    get_interaction_stats,
    update_interaction_stat,
    delete_interaction_stat,
)
from routes.dependencies import require_roles

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
    return create_interaction_stat(db, data)


@router.get("/", response_model=list[InteractionStatResponse])
def list_interaction_stats_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return get_interaction_stats(db, skip=skip, limit=limit)


@router.get("/{interaction_stat_id}", response_model=InteractionStatResponse)
def get_interaction_stat_endpoint(
    interaction_stat_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_interaction_stat_by_id(db, interaction_stat_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="InteractionStat not found")
    return db_obj


@router.put("/{interaction_stat_id}", response_model=InteractionStatResponse)
def update_interaction_stat_endpoint(
    interaction_stat_id: int,
    data: InteractionStatUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = update_interaction_stat(db, interaction_stat_id, data)
    if not db_obj:
        raise HTTPException(status_code=404, detail="InteractionStat not found")
    return db_obj


@router.delete("/{interaction_stat_id}")
def delete_interaction_stat_endpoint(
    interaction_stat_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    deleted = delete_interaction_stat(db, interaction_stat_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="InteractionStat not found")
    return {"message": "InteractionStat deleted successfully"}
