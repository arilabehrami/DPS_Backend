from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.session import Session as UserSession
from schemas.session import SessionCreate, SessionUpdate, SessionResponse
from services.session import (
    create_session,
    get_session_by_id,
    get_sessions,
    update_session,
    delete_session,
)
from routes.dependencies import require_roles
from security.tenant import ensure_user_access

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
    ensure_user_access(db, data.user_id, current_user)
    return create_session(db, data)


@router.get("/", response_model=list[SessionResponse])
def list_sessions_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return (
        db.query(UserSession)
        .filter(UserSession.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{session_id}", response_model=SessionResponse)
def get_session_endpoint(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_session_by_id(db, session_id)
    if not db_obj or db_obj.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_obj


@router.put("/{session_id}", response_model=SessionResponse)
def update_session_endpoint(
    session_id: int,
    data: SessionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = get_session_by_id(db, session_id)
    if not db_obj or db_obj.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    if data.user_id is not None:
        ensure_user_access(db, data.user_id, current_user)
    db_obj = update_session(db, session_id, data)
    return db_obj


@router.delete("/{session_id}")
def delete_session_endpoint(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = get_session_by_id(db, session_id)
    if not db_obj or db_obj.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    deleted = delete_session(db, session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}
