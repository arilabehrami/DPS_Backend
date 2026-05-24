from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas.experiment import ExperimentCreate, ExperimentUpdate, ExperimentResponse
from services.experiment import (
    create_experiment,
    get_experiment_by_id,
    get_experiments,
    update_experiment,
    delete_experiment,
)
from routes.dependencies import require_roles

router = APIRouter(
    prefix="/experiments",
    tags=["Experiments"],
)


@router.post("/", response_model=ExperimentResponse)
def create_experiment_endpoint(
    data: ExperimentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    return create_experiment(db, data)


@router.get("/", response_model=list[ExperimentResponse])
def list_experiments_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return get_experiments(db, skip=skip, limit=limit)


@router.get("/{experiment_id}", response_model=ExperimentResponse)
def get_experiment_endpoint(
    experiment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_experiment_by_id(db, experiment_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return db_obj


@router.put("/{experiment_id}", response_model=ExperimentResponse)
def update_experiment_endpoint(
    experiment_id: int,
    data: ExperimentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = update_experiment(db, experiment_id, data)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return db_obj


@router.delete("/{experiment_id}")
def delete_experiment_endpoint(
    experiment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    deleted = delete_experiment(db, experiment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return {"message": "Experiment deleted successfully"}
