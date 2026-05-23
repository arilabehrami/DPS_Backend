from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.interaction_stats import InteractionStats
from models.user import User
from security.auth_security import get_current_user
from security.tenant import ensure_persona_access, ensure_user_access
from schemas.interaction_stats import InteractionStatsCreate, InteractionStatsUpdate, InteractionStatsResponse
from services.interaction_stats import (
    create_interaction_stats,
    get_interaction_stats,
    get_interaction_stats_by_id,
    get_interaction_stats_by_user_id,
    get_interaction_stats_by_persona_id,
    update_interaction_stats,
    delete_interaction_stats
)

router = APIRouter(
    prefix="/interaction-stats",
    tags=["Interaction Stats"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=InteractionStatsResponse)
def create_interaction_stats_endpoint(
    data: InteractionStatsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_user_access(db, data.user_id, current_user)
    if data.persona_id is not None:
        ensure_persona_access(db, data.persona_id, current_user)
    return create_interaction_stats(db, data)


@router.get("/", response_model=list[InteractionStatsResponse])
def get_interaction_stats_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(InteractionStats)
        .join(User, InteractionStats.user_id == User.id)
        .filter(User.workspace_id == current_user.workspace_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{stats_id}", response_model=InteractionStatsResponse)
def get_interaction_stats_endpoint_by_id(
    stats_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stats = get_interaction_stats_by_id(db, stats_id)

    if not stats:
        raise HTTPException(status_code=404, detail="Interaction stats not found")

    ensure_user_access(db, stats.user_id, current_user)
    if stats.persona_id is not None:
        ensure_persona_access(db, stats.persona_id, current_user)

    return stats


@router.get("/user/{user_id}", response_model=list[InteractionStatsResponse])
def get_interaction_stats_by_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_user_access(db, user_id, current_user)
    return get_interaction_stats_by_user_id(db, user_id)


@router.get("/persona/{persona_id}", response_model=list[InteractionStatsResponse])
def get_interaction_stats_by_persona_endpoint(
    persona_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_persona_access(db, persona_id, current_user)
    return get_interaction_stats_by_persona_id(db, persona_id)


@router.put("/{stats_id}", response_model=InteractionStatsResponse)
def update_interaction_stats_endpoint(
    stats_id: int,
    data: InteractionStatsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stats = get_interaction_stats_by_id(db, stats_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Interaction stats not found")

    ensure_user_access(db, stats.user_id, current_user)
    stats = update_interaction_stats(db, stats_id, data)

    if not stats:
        raise HTTPException(status_code=404, detail="Interaction stats not found")

    return stats


@router.delete("/{stats_id}")
def delete_interaction_stats_endpoint(
    stats_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stats = get_interaction_stats_by_id(db, stats_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Interaction stats not found")

    ensure_user_access(db, stats.user_id, current_user)
    stats = delete_interaction_stats(db, stats_id)

    if not stats:
        raise HTTPException(status_code=404, detail="Interaction stats not found")

    return {"message": "Interaction stats deleted successfully"}
