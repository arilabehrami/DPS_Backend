from sqlalchemy.orm import Session
from models.experiment import Experiment
from schemas.experiment import ExperimentCreate, ExperimentUpdate


def create_experiment(db: Session, data: ExperimentCreate) -> Experiment:
    db_obj = Experiment(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_experiment_by_id(db: Session, experiment_id: int) -> Experiment | None:
    return db.query(Experiment).filter(Experiment.id == experiment_id).first()


def get_experiments(db: Session, skip: int = 0, limit: int = 100) -> list[Experiment]:
    return db.query(Experiment).offset(skip).limit(limit).all()


def update_experiment(db: Session, experiment_id: int, data: ExperimentUpdate) -> Experiment | None:
    db_obj = get_experiment_by_id(db, experiment_id)
    if not db_obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_experiment(db: Session, experiment_id: int) -> bool:
    db_obj = get_experiment_by_id(db, experiment_id)
    if not db_obj:
        return False

    db.delete(db_obj)
    db.commit()
    return True
