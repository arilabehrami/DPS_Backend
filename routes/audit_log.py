from fastapi import APIRouter

router = APIRouter(prefix="/audit-log", tags=["AuditLog"])


@router.get("/")
def get_logs():
    return {"message": "Audit log endpoint working"}