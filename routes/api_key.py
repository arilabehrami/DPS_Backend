from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.api_key import APIKey
from models.user import User
from security.auth_security import require_roles
from security.tenant import ensure_user_access
from schemas.api_key import APIKeyCreate, APIKeyUpdate, APIKeyResponse
from services.api_key import (
    create_api_key,
    get_api_keys,
    get_api_key_by_id,
    get_api_keys_by_user_id,
    update_api_key,
    delete_api_key
)

router = APIRouter(
    prefix="/api-keys",
    tags=["API Keys"],
    dependencies=[Depends(require_roles("admin"))],
)


@router.post("/", response_model=APIKeyResponse)
def create_api_key_endpoint(
    data: APIKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    if data.user_id is not None:
        ensure_user_access(db, data.user_id, current_user)
    return create_api_key(db, data)


@router.get("/", response_model=list[APIKeyResponse])
def get_api_keys_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return (
        db.query(APIKey)
        .join(User, APIKey.user_id == User.id)
        .filter(User.workspace_id == current_user.workspace_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{api_key_id}", response_model=APIKeyResponse)
def get_api_key_endpoint(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    api_key = get_api_key_by_id(db, api_key_id)

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    if api_key.user_id is not None:
        ensure_user_access(db, api_key.user_id, current_user)

    return api_key


@router.get("/user/{user_id}", response_model=list[APIKeyResponse])
def get_api_keys_by_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    ensure_user_access(db, user_id, current_user)
    return get_api_keys_by_user_id(db, user_id)


@router.put("/{api_key_id}", response_model=APIKeyResponse)
def update_api_key_endpoint(
    api_key_id: int,
    data: APIKeyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    api_key = get_api_key_by_id(db, api_key_id)
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    if api_key.user_id is not None:
        ensure_user_access(db, api_key.user_id, current_user)

    api_key = update_api_key(db, api_key_id, data)

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    return api_key


@router.delete("/{api_key_id}")
def delete_api_key_endpoint(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    api_key = get_api_key_by_id(db, api_key_id)
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    if api_key.user_id is not None:
        ensure_user_access(db, api_key.user_id, current_user)

    api_key = delete_api_key(db, api_key_id)

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    return {"message": "API key deleted successfully"}
