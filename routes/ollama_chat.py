from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel

from routes.dependencies import require_roles
from services.background_jobs import record_event_log
from services.cache import cache_service
from services.llm_service import llm_service

router = APIRouter(prefix="/ollama", tags=["Ollama / LLM"])


class OllamaChatRequest(BaseModel):
    message: str
    system_prompt: str | None = None
    model: str | None = None


@router.post("/chat")
def ollama_chat(
    data: OllamaChatRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(require_roles("admin", "employee", "client")),
):
    cache_key = f"llm:v2:{current_user.workspace_id}:{data.model or 'default'}:{data.message}"
    cached = cache_service.get(cache_key)
    if cached:
        return {"response": cached["response"], "cached": True}

    response = llm_service.generate(data.message, data.system_prompt, data.model)
    if not llm_service.is_unreachable_response(response):
        cache_service.set(cache_key, {"response": response}, ttl_seconds=300)
    background_tasks.add_task(
        record_event_log,
        current_user.id,
        current_user.workspace_id,
        "llm_chat",
        data.message[:255],
    )
    return {"response": response, "cached": False}
