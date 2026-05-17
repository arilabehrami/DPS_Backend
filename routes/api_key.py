from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.api_key import APIKeyCreate, APIKeyUpdate, APIKeyResponse
from services.api_key import (
    create_api_key,
    get_api_keys,
    get_api_key_by_id,
    get_api_keys_by_user_id,
    update_api_key,
    delete_api_key
)

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


@router.post("/", response_model=APIKeyResponse)
def create_api_key_endpoint(data: APIKeyCreate, db: Session = Depends(get_db)):
    return create_api_key(db, data)


@router.get("/", response_model=list[APIKeyResponse])
def get_api_keys_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_api_keys(db, skip, limit)


@router.get("/{api_key_id}", response_model=APIKeyResponse)
def get_api_key_endpoint(api_key_id: int, db: Session = Depends(get_db)):
    api_key = get_api_key_by_id(db, api_key_id)

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    return api_key


@router.get("/user/{user_id}", response_model=list[APIKeyResponse])
def get_api_keys_by_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    return get_api_keys_by_user_id(db, user_id)


@router.put("/{api_key_id}", response_model=APIKeyResponse)
def update_api_key_endpoint(api_key_id: int, data: APIKeyUpdate, db: Session = Depends(get_db)):
    api_key = update_api_key(db, api_key_id, data)

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    return api_key


@router.delete("/{api_key_id}")
def delete_api_key_endpoint(api_key_id: int, db: Session = Depends(get_db)):
    api_key = delete_api_key(db, api_key_id)

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    return {"message": "API key deleted successfully"}