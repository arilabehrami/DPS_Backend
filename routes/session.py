from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas.session import SessionCreate, SessionUpdate, SessionResponse
from services.session import (
    create_session,
    get_session_by_id,
    get_sessions,
    update_session,
    delete_session,
)
from routes.dependencies import require_roles

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
)


@router.post("/", response_model=SessionResponse)
def create_session_endpoint(
    data: SessionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    return create_session(db, data)


@router.get("/", response_model=list[SessionResponse])
def list_sessions_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return get_sessions(db, skip=skip, limit=limit)


@router.get("/{session_id}", response_model=SessionResponse)
def get_session_endpoint(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_session_by_id(db, session_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_obj


@router.put("/{session_id}", response_model=SessionResponse)
def update_session_endpoint(
    session_id: int,
    data: SessionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = update_session(db, session_id, data)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_obj


@router.delete("/{session_id}")
def delete_session_endpoint(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    deleted = delete_session(db, session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}
