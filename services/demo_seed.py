import logging
import os

from sqlalchemy.orm import Session

from models.conversation import Conversation
from models.persona import Persona
from models.persona_trait import PersonaTrait
from models.role import Role
from models.user import User
from models.workspace import Workspace
from security.auth_security import hash_password


logger = logging.getLogger("demo_seed")


def seed_demo_data(db: Session) -> None:
    if os.getenv("SEED_DEMO_DATA", "true").lower() not in {"1", "true", "yes"}:
        return

    workspace = db.query(Workspace).filter(Workspace.name == "Default Workspace").first()
    if not workspace:
        workspace = Workspace(name="Default Workspace")
        db.add(workspace)
        db.commit()
        db.refresh(workspace)

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

    admin_user = db.query(User).filter(User.email == "admin@dps.com").first()
    if not admin_user:
        admin_user = User(
            workspace_id=workspace.id,
            role_id=admin_role.id,
            username="admin",
            email="admin@dps.com",
            hashed_password=hash_password("admin123"),
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

    persona = db.query(Persona).filter(Persona.name == "Aura").first()
    if not persona:
        persona = Persona(
            workspace_id=workspace.id,
            user_id=admin_user.id,
            name="Aura",
            description="Friendly virtual personality for interview practice and feedback.",
        )
        db.add(persona)
        db.commit()
        db.refresh(persona)

    existing_trait = db.query(PersonaTrait).filter(PersonaTrait.persona_id == persona.id).first()
    if not existing_trait:
        db.add_all(
            [
                PersonaTrait(persona_id=persona.id, trait_name="tone", value="friendly"),
                PersonaTrait(persona_id=persona.id, trait_name="style", value="supportive"),
                PersonaTrait(persona_id=persona.id, trait_name="goal", value="help users practice conversations"),
            ]
        )
        db.commit()

    conversation = db.query(Conversation).filter(
        Conversation.title == "Demo Conversation",
        Conversation.user_id == admin_user.id
    ).first()

    if not conversation:
        conversation = Conversation(
            workspace_id=workspace.id,
            user_id=admin_user.id,
            persona_id=persona.id,
            title="Demo Conversation",
        )
        db.add(conversation)
        db.commit()

    logger.info("Demo data ready.")