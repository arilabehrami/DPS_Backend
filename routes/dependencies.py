import os
from typing import Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from database import get_db
from models.user import User

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


ROLE_ALIASES = {
    "user": "client",
    "client": "client",
    "employ": "employee",
    "administrator": "admin",
}

ROLE_PERMISSIONS = {
    "admin": {
        "view_users",
        "view_allowed_recipients",
        "delete_user",
        "update_role",
        "create_admin",
    },
    "employee": {
        "view_users",
        "view_allowed_recipients",
        "delete_user",
    },
    "client": {
        "view_users",
        "view_allowed_recipients",
    },
}


def normalize_role_name(role_name: str | None) -> str:
    role = (role_name or "guest").lower()
    return ROLE_ALIASES.get(role, role)


def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    current_user = getattr(request.state, "current_user", None)
    if current_user is not None:
        return current_user

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user


def require_roles(*allowed_roles: str) -> Callable:
    def checker(current_user: User = Depends(get_current_user)) -> User:
        role_name = normalize_role_name(current_user.role.name if current_user.role else None)
        normalized = {normalize_role_name(role) for role in allowed_roles}
        if role_name not in normalized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )
        return current_user

    return checker


def require_permissions(*required_permissions: str) -> Callable:
    def checker(current_user: User = Depends(get_current_user)) -> User:
        role_name = normalize_role_name(current_user.role.name if current_user.role else None)
        granted_permissions = ROLE_PERMISSIONS.get(role_name, set())

        for permission in required_permissions:
            if permission not in granted_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"missing permission: {permission}",
                )
        return current_user

    return checker
