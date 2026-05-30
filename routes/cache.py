from fastapi import APIRouter, Depends

from routes.dependencies import require_roles
from services.cache import cache_service

router = APIRouter(prefix="/cache", tags=["Caching"])


@router.get("/status")
def cache_status(current_user=Depends(require_roles("admin", "user"))):
    return {"backend": cache_service.backend, "enabled": True}
