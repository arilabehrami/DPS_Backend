from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/")
def get_settings():
    return {"message": "Settings endpoint working"}