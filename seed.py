from database import Base, engine, SessionLocal

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

Base.metadata.create_all(bind=engine)

db = SessionLocal()

role = db.query(Role).filter(Role.name == "admin").first()
if not role:
    role = Role(name="admin")
    db.add(role)

workspace = db.query(Workspace).filter(Workspace.name == "Default Workspace").first()
if not workspace:
    workspace = Workspace(name="Default Workspace")
    db.add(workspace)

db.commit()
db.close()

print("Seed completed successfully.")