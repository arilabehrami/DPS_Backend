from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel, EmailStr

from routes.dependencies import require_roles
from services.background_jobs import record_event_log

router = APIRouter(prefix="/background-jobs", tags=["Background Jobs"])


class EmailJobRequest(BaseModel):
    email: EmailStr
    subject: str
    content: str


@router.post("/email-demo")
def queue_email_demo(
    data: EmailJobRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(require_roles("admin")),
):
    background_tasks.add_task(
        record_event_log,
        current_user.id,
        current_user.workspace_id,
        "email_demo_queued",
        f"Queued email to {data.email}: {data.subject}",
    )
    return {"message": "Background email job queued"}
