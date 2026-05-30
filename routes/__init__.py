from routes.auth import router as auth_router
from routes.background_job import router as background_job_router
from routes.cache import router as cache_router
from routes.chat import router as chat_router
from routes.conversation import router as conversation_router
from routes.event_log import router as event_log_router
from routes.feedback import router as feedback_router
from routes.message import router as message_router
from routes.notification import router as notification_router
from routes.ollama_chat import router as ollama_chat_router
from routes.persona import router as persona_router
from routes.personality import router as personality_router
from routes.rating import router as rating_router
from routes.role import router as role_router
from routes.user import router as user_router
from routes.workspace import router as workspace_router

ALL_ROUTERS = [
    auth_router,
    background_job_router,
    cache_router,
    chat_router,
    conversation_router,
    event_log_router,
    feedback_router,
    message_router,
    notification_router,
    ollama_chat_router,
    persona_router,
    personality_router,
    rating_router,
    role_router,
    user_router,
    workspace_router,
]
