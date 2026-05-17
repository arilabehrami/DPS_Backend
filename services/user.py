from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate, UserUpdate


def create_user(db: Session, data: UserCreate):
    user = User(**data.dict(exclude_unset=True))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_users_by_workspace_id(db: Session, workspace_id: int):
    return db.query(User).filter(User.workspace_id == workspace_id).all()


def get_users_by_role_id(db: Session, role_id: int):
    return db.query(User).filter(User.role_id == role_id).all()


def update_user(db: Session, user_id: int, data: UserUpdate):
    user = get_user_by_id(db, user_id)

    if not user:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)

    if not user:
        return None

    db.delete(user)
    db.commit()
    return user