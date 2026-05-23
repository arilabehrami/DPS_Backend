from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from database import get_db
from models.session import Session as UserSession
from models.user import User
from security.auth_security import get_current_user
from security.tenant import ensure_user_access
from schemas.session import SessionCreate, SessionUpdate, SessionResponse
from services.session import (
    create_session,
    get_sessions,
    get_session_by_id,
    get_sessions_by_user_id,
    update_session,
    delete_session,
    delete_sessions_by_user_id
)

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=SessionResponse)
def create_session_endpoint(
    data: SessionCreate,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.user_id is not None:
        ensure_user_access(db, data.user_id, current_user)
    return create_session(db, data)


@router.get("/", response_model=list[SessionResponse])
def get_sessions_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(UserSession)
        .join(User, UserSession.user_id == User.id)
        .filter(User.workspace_id == current_user.workspace_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{session_id}", response_model=SessionResponse)
def get_session_endpoint(
    session_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = get_session_by_id(db, session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.user_id is not None:
        ensure_user_access(db, session.user_id, current_user)

    return session


@router.get("/user/{user_id}", response_model=list[SessionResponse])
def get_sessions_by_user_endpoint(
    user_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_user_access(db, user_id, current_user)
    return get_sessions_by_user_id(db, user_id)


@router.put("/{session_id}", response_model=SessionResponse)
def update_session_endpoint(
    session_id: int,
    data: SessionUpdate,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.user_id is not None:
        ensure_user_access(db, session.user_id, current_user)

    session = update_session(db, session_id, data)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session


@router.delete("/{session_id}")
def delete_session_endpoint(
    session_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.user_id is not None:
        ensure_user_access(db, session.user_id, current_user)

    session = delete_session(db, session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"message": "Session deleted successfully"}


@router.delete("/user/{user_id}")
def delete_sessions_by_user_endpoint(
    user_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_user_access(db, user_id, current_user)
    deleted_sessions = delete_sessions_by_user_id(db, user_id)

    return {
        "message": "User sessions deleted successfully",
        "deleted_count": len(deleted_sessions)
    }
