from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine


from models.ai_response import AIResponse
from models.api_key import APIKey
from models.audit_log import AuditLog
from models.chat_message import ChatMessage
from models.conversation import Conversation
from models.event_log import EventLog
from models.feedback import Feedback
from models.interaction_stats import InteractionStats
from models.message import Message
from models.notification import Notification
from models.persona_history import PersonaHistory
from models.persona_trait import PersonaTrait
from models.persona import Persona
from models.personality import Personality
from models.prompt_template import PromptTemplate
from models.role import Role
from models.session import Session
from models.settings import Settings
from models.user import User
from models.workspace import Workspace


from routes.ai_response import router as ai_response_router
from routes.api_key import router as api_key_router
from routes.audit_log import router as audit_log_router
from routes.chat_message import router as chat_message_router
from routes.conversation import router as conversation_router
from routes.event_log import router as event_log_router
from routes.feedback import router as feedback_router
from routes.interaction_stats import router as interaction_stats_router
from routes.message import router as message_router
from routes.notification import router as notification_router
from routes.persona_history import router as persona_history_router
from routes.persona_trait import router as persona_trait_router
from routes.persona import router as persona_router
from routes.personality import router as personality_router
from routes.prompt_template import router as prompt_template_router
from routes.role import router as role_router
from routes.session import router as session_router
from routes.settings import router as settings_router
from routes.user import router as user_router
from routes.workspace import router as workspace_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Digital Personality Simulator API",
    description="Backend API for Digital Personality Simulator project",
    version="1.0.0"
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def root():
    return {
        "message": "Digital Personality Simulator API is running successfully"
    }



app.include_router(ai_response_router)
app.include_router(api_key_router)
app.include_router(audit_log_router)
app.include_router(chat_message_router)
app.include_router(conversation_router)
app.include_router(event_log_router)
app.include_router(feedback_router)
app.include_router(interaction_stats_router)
app.include_router(message_router)
app.include_router(notification_router)
app.include_router(persona_history_router)
app.include_router(persona_trait_router)
app.include_router(persona_router)
app.include_router(personality_router)
app.include_router(prompt_template_router)
app.include_router(role_router)
app.include_router(session_router)
app.include_router(settings_router)
app.include_router(user_router)
app.include_router(workspace_router)