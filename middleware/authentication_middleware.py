import os

from jose import JWTError, jwt
from sqlalchemy.orm import joinedload
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from database import SessionLocal
from models.user import User


SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.current_user = None

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.removeprefix("Bearer ").strip()
            if token:
                try:
                    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                    user_id = payload.get("sub")
                    if user_id is not None:
                        db = SessionLocal()
                        try:
                            user = (
                                db.query(User)
                                .options(joinedload(User.role))
                                .filter(User.id == int(user_id))
                                .first()
                            )
                            if user is not None:
                                request.state.current_user = user
                        finally:
                            db.close()
                except (JWTError, ValueError):
                    # Invalid token is handled by route dependencies on protected endpoints.
                    pass

        return await call_next(request)
