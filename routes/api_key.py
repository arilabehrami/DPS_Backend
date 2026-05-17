from fastapi import APIRouter

router = APIRouter(prefix="/api-keys", tags=["APIKey"])


@router.get("/")
def get_keys():
    return {"message": "API keys endpoint working"}