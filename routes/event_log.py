from fastapi import APIRouter

router = APIRouter(prefix="/event-log", tags=["EventLog"])


@router.get("/")
def get_events():
    return {"message": "Event log working"}