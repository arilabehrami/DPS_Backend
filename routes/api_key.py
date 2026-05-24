from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas.api_key import ApiKeyCreate, ApiKeyUpdate, ApiKeyResponse
from services.api_key import (
    create_api_key,
    get_api_key_by_id,
    get_api_keys,
    update_api_key,
    delete_api_key,
)
from routes.dependencies import require_roles

router = APIRouter(
    prefix="/api-keys",
    tags=["Api Keys"],
)


@router.post("/", response_model=ApiKeyResponse)
def create_api_key_endpoint(
    data: ApiKeyCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    return create_api_key(db, data)


@router.get("/", response_model=list[ApiKeyResponse])
def list_api_keys_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    return get_api_keys(db, skip=skip, limit=limit)


@router.get("/{api_key_id}", response_model=ApiKeyResponse)
def get_api_key_endpoint(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "user")),
):
    db_obj = get_api_key_by_id(db, api_key_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="ApiKey not found")
    return db_obj


@router.put("/{api_key_id}", response_model=ApiKeyResponse)
def update_api_key_endpoint(
    api_key_id: int,
    data: ApiKeyUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    db_obj = update_api_key(db, api_key_id, data)
    if not db_obj:
        raise HTTPException(status_code=404, detail="ApiKey not found")
    return db_obj


@router.delete("/{api_key_id}")
def delete_api_key_endpoint(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    deleted = delete_api_key(db, api_key_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="ApiKey not found")
    return {"message": "ApiKey deleted successfully"}
