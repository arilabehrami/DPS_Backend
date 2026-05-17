from sqlalchemy.orm import Session as DBSession
from models.session import Session as UserSession
from schemas.session import SessionCreate, SessionUpdate


def create_session(db: DBSession, data: SessionCreate):
    session = UserSession(**data.dict(exclude_unset=True))
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_sessions(db: DBSession, skip: int = 0, limit: int = 100):
    return db.query(UserSession).offset(skip).limit(limit).all()


def get_session_by_id(db: DBSession, session_id: int):
    return db.query(UserSession).filter(UserSession.id == session_id).first()


def get_sessions_by_user_id(db: DBSession, user_id: int):
    return db.query(UserSession).filter(UserSession.user_id == user_id).all()


def update_session(db: DBSession, session_id: int, data: SessionUpdate):
    session = get_session_by_id(db, session_id)

    if not session:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(session, field, value)

    db.commit()
    db.refresh(session)
    return session


def delete_session(db: DBSession, session_id: int):
    session = get_session_by_id(db, session_id)

    if not session:
        return None

    db.delete(session)
    db.commit()
    return session


def delete_sessions_by_user_id(db: DBSession, user_id: int):
    sessions = get_sessions_by_user_id(db, user_id)

    for session in sessions:
        db.delete(session)

    db.commit()
    return sessions