from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.experiment import Experiment
from schemas.experiment import ExperimentCreate, ExperimentUpdate, ExperimentResponse
from services.experiment import (
    create_experiment,
    get_experiment_by_id,
    get_experiments,
    update_experiment,
    delete_experiment,
)
from routes.dependencies import require_roles
from security.tenant import ensure_conversation_access, ensure_personality_access, ensure_user_access, ensure_workspace_access

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
    ensure_workspace_access(data.workspace_id, current_user)
    ensure_user_access(db, data.user_id, current_user)
    if data.personality_id is not None:
        ensure_personality_access(db, data.personality_id, current_user)
    if data.conversation_id is not None:
        ensure_conversation_access(db, data.conversation_id, current_user)
    return create_experiment(db, data)


@router.get("/", response_model=list[ExperimentResponse])
def list_experiments_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return db.query(Experiment).filter(Experiment.workspace_id == current_user.workspace_id).offset(skip).limit(limit).all()


@router.get("/{experiment_id}", response_model=ExperimentResponse)
def get_experiment_endpoint(
    experiment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_experiment_by_id(db, experiment_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return db_obj


@router.put("/{experiment_id}", response_model=ExperimentResponse)
def update_experiment_endpoint(
    experiment_id: int,
    data: ExperimentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = get_experiment_by_id(db, experiment_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="Experiment not found")
    if data.workspace_id is not None:
        ensure_workspace_access(data.workspace_id, current_user)
    if data.user_id is not None:
        ensure_user_access(db, data.user_id, current_user)
    if data.personality_id is not None:
        ensure_personality_access(db, data.personality_id, current_user)
    if data.conversation_id is not None:
        ensure_conversation_access(db, data.conversation_id, current_user)
    db_obj = update_experiment(db, experiment_id, data)
    return db_obj


@router.delete("/{experiment_id}")
def delete_experiment_endpoint(
    experiment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = get_experiment_by_id(db, experiment_id)
    if not db_obj or db_obj.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=404, detail="Experiment not found")
    deleted = delete_experiment(db, experiment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return {"message": "Experiment deleted successfully"}
