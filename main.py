from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine

from models.user import User
from models.role import Role
from models.workspace import Workspace
from models.personality import Personality
from models.persona import Persona
from models.conversation import Conversation
from models.message import Message
from models.chat_message import ChatMessage
from models.settings import Settings
from models.audit_log import AuditLog
from models.api_key import APIKey
from models.event_log import EventLog
from models.prompt_template import PromptTemplate
from models.persona_history import PersonaHistory
from models.interaction_stats import InteractionStats



optional_models = {}

try:
    from models.session import Session as DBSession
    optional_models["session"] = DBSession
except:
    optional_models["session"] = None

try:
    from models.notification import Notification
    optional_models["notification"] = Notification
except:
    optional_models["notification"] = None

try:
    from models.feedback import Feedback
    optional_models["feedback"] = Feedback
except:
    optional_models["feedback"] = None

try:
    from models.persona_trait import PersonaTrait
    optional_models["persona_trait"] = PersonaTrait
except:
    optional_models["persona_trait"] = None

try:
    from models.ai_response import AIResponse
    optional_models["ai_response"] = AIResponse
except:
    optional_models["ai_response"] = None






app = FastAPI(
    title="Digital Personality Simulator",
    description="Backend API for users, personas, conversations and AI system",
    version="1.0.0"
)


# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# ROUTES
# =========================
from routes.auth import router as auth_router
from routes.user import router as user_router
from routes.role import router as role_router
from routes.workspace import router as workspace_router
from routes.personality import router as personality_router
from routes.persona import router as persona_router
from routes.conversation import router as conversation_router
from routes.message import router as message_router
from routes.chat import router as chat_router

from routes.chat_message import router as chatmessage_router
from routes.settings import router as settings_router
from routes.audit_log import router as auditlog_router
from routes.api_key import router as apikey_router
from routes.event_log import router as eventlog_router

from routes.prompt_template import router as promptTemplate_router
from routes.persona_history import router as personaHistory_router
from routes.interaction_stats import router as interactionStats_router


# =========================
# OPTIONAL ROUTES SAFE LOAD
# =========================
def safe_import(path, name):
    try:
        module = __import__(path, fromlist=[name])
        return getattr(module, name)
    except:
        return None


session_router = safe_import("routes.session", "router")
notification_router = safe_import("routes.notification", "router")
feedback_router = safe_import("routes.feedback", "router")
persona_trait_router = safe_import("routes.persona_trait", "router")
ai_response_router = safe_import("routes.ai_response", "router")


# =========================
# INCLUDE ROUTERS
# =========================
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(role_router)
app.include_router(workspace_router)
app.include_router(personality_router)
app.include_router(persona_router)
app.include_router(conversation_router)
app.include_router(message_router)
app.include_router(chat_router)

app.include_router(chatmessage_router)
app.include_router(settings_router)
app.include_router(auditlog_router)
app.include_router(apikey_router)
app.include_router(eventlog_router)
app.include_router(promptTemplate_router)
app.include_router(personaHistory_router)
app.include_router(interactionStats_router)


# OPTIONAL INCLUDE
if session_router:
    app.include_router(session_router)

if notification_router:
    app.include_router(notification_router)

if feedback_router:
    app.include_router(feedback_router)

if persona_trait_router:
    app.include_router(persona_trait_router)

if ai_response_router:
    app.include_router(ai_response_router)


# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def home():
    return {"message": "Backend is alive"}