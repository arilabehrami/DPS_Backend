from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
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

router = APIRouter(prefix="/interaction-stats", tags=["Interaction Stats"])


@router.post("/", response_model=InteractionStatsResponse)
def create_interaction_stats_endpoint(data: InteractionStatsCreate, db: Session = Depends(get_db)):
    return create_interaction_stats(db, data)


@router.get("/", response_model=list[InteractionStatsResponse])
def get_interaction_stats_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_interaction_stats(db, skip, limit)


@router.get("/{stats_id}", response_model=InteractionStatsResponse)
def get_interaction_stats_endpoint_by_id(stats_id: int, db: Session = Depends(get_db)):
    stats = get_interaction_stats_by_id(db, stats_id)

    if not stats:
        raise HTTPException(status_code=404, detail="Interaction stats not found")

    return stats


@router.get("/user/{user_id}", response_model=list[InteractionStatsResponse])
def get_interaction_stats_by_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    return get_interaction_stats_by_user_id(db, user_id)


@router.get("/persona/{persona_id}", response_model=list[InteractionStatsResponse])
def get_interaction_stats_by_persona_endpoint(persona_id: int, db: Session = Depends(get_db)):
    return get_interaction_stats_by_persona_id(db, persona_id)


@router.put("/{stats_id}", response_model=InteractionStatsResponse)
def update_interaction_stats_endpoint(stats_id: int, data: InteractionStatsUpdate, db: Session = Depends(get_db)):
    stats = update_interaction_stats(db, stats_id, data)

    if not stats:
        raise HTTPException(status_code=404, detail="Interaction stats not found")

    return stats


@router.delete("/{stats_id}")
def delete_interaction_stats_endpoint(stats_id: int, db: Session = Depends(get_db)):
    stats = delete_interaction_stats(db, stats_id)

    if not stats:
        raise HTTPException(status_code=404, detail="Interaction stats not found")

    return {"message": "Interaction stats deleted successfully"}