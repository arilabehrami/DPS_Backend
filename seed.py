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

from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # =========================
    # ROLES
    # =========================
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        admin_role = Role(name="admin")
        db.add(admin_role)
        db.commit()
        db.refresh(admin_role)

    user_role = db.query(Role).filter(Role.name == "user").first()
    if not user_role:
        user_role = Role(name="user")
        db.add(user_role)
        db.commit()
        db.refresh(user_role)

    # =========================
    # DEFAULT WORKSPACE
    # =========================
    workspace = db.query(Workspace).filter(Workspace.name == "Default Workspace").first()
    if not workspace:
        workspace = Workspace(name="Default Workspace")
        db.add(workspace)
        db.commit()
        db.refresh(workspace)

    # =========================
    # DEFAULT ADMIN USER
    # =========================
    admin_user = db.query(User).filter(User.email == "admin@dps.com").first()

    if not admin_user:
        admin_user = User(
            full_name="Admin User",
            username="admin",
            email="admin@dps.com",
            hashed_password=hash_password("admin123"),
            workspace_id=workspace.id,
            role_id=admin_role.id,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
    else:
        admin_user.workspace_id = workspace.id
        admin_user.role_id = admin_role.id

        if hasattr(admin_user, "username") and not admin_user.username:
            admin_user.username = "admin"

        if hasattr(admin_user, "full_name") and not admin_user.full_name:
            admin_user.full_name = "Admin User"

        db.commit()

    # =========================
    # DEFAULT PERSONA - AURA
    # =========================
    aura = db.query(Persona).filter(Persona.name == "Aura").first()

    if not aura:
        aura = Persona(
            name="Aura",
            description="Helpful AI assistant for the Digital Personality Simulator.",
            workspace_id=workspace.id,
        )
        db.add(aura)
        db.commit()
        db.refresh(aura)
    else:
        aura.workspace_id = workspace.id

        if hasattr(aura, "description") and not aura.description:
            aura.description = "Helpful AI assistant for the Digital Personality Simulator."

        db.commit()

    # =========================
    # FIX ALL EXISTING USERS
    # =========================
    users = db.query(User).all()

    for user in users:
        user.workspace_id = workspace.id

        if user.email == "admin@dps.com":
            user.role_id = admin_role.id
        elif not user.role_id:
            user.role_id = user_role.id

    db.commit()

    # =========================
    # FIX ALL EXISTING PERSONAS
    # =========================
    personas = db.query(Persona).all()

    for persona in personas:
        persona.workspace_id = workspace.id

    db.commit()

    # =========================
    # FIX ALL EXISTING CONVERSATIONS
    # =========================
    if hasattr(Conversation, "workspace_id"):
        conversations = db.query(Conversation).all()

        for conversation in conversations:
            conversation.workspace_id = workspace.id

        db.commit()

    # =========================
    # FIX CHAT MESSAGES IF THEY HAVE WORKSPACE_ID
    # =========================
    if hasattr(ChatMessage, "workspace_id"):
        chat_messages = db.query(ChatMessage).all()

        for chat_message in chat_messages:
            chat_message.workspace_id = workspace.id

        db.commit()

    # =========================
    # FIX MESSAGES IF THEY HAVE WORKSPACE_ID
    # =========================
    if hasattr(Message, "workspace_id"):
        messages = db.query(Message).all()

        for message in messages:
            message.workspace_id = workspace.id

        db.commit()

    print("Seed completed successfully.")
    print("--------------------------------")
    print(f"Workspace: {workspace.name}")
    print(f"Workspace ID: {workspace.id}")
    print("Admin email: admin@dps.com")
    print("Admin password: admin123")
    print(f"Aura Persona ID: {aura.id}")
    print("--------------------------------")
    print("All users, personas, and conversations were assigned to the Default Workspace.")

except Exception as e:
    db.rollback()
    print("Seed failed.")
    print(str(e))

finally:
    db.close()