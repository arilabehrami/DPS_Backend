from fastapi import APIRouter

router = APIRouter(prefix="/interaction-stats", tags=["InteractionStats"])


@router.get("/")
def get_stats():
    return {"message": "Interaction stats working"}