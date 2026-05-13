from fastapi import APIRouter, Depends

from models.user import User
from schemas.user import UserResponse
from security.auth_security import get_current_user


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user