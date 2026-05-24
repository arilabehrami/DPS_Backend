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

    workspace = db.query(Workspace).filter(Workspace.id == 1).first()
    if not workspace:
        workspace = Workspace(id=1, name="Default Workspace")
        db.add(workspace)

    admin_role = db.query(Role).filter(Role.id == 1).first()
    if not admin_role:
        admin_role = Role(id=1, name="admin")
        db.add(admin_role)

    user_role = db.query(Role).filter(Role.name == "user").first()
    if not user_role:
        user_role = Role(name="user")
        db.add(user_role)

    db.commit()

    admin_user = db.query(User).filter(User.id == 1).first()
    if not admin_user:
        admin_user = User(
            id=1,
            workspace_id=workspace.id,
            role_id=admin_role.id,
            username="admin",
            email="admin@dps.com",
            hashed_password=hash_password("admin123"),
        )
        db.add(admin_user)
        db.commit()

    persona = db.query(Persona).filter(Persona.id == 1).first()
    if not persona:
        persona = Persona(
            id=1,
            workspace_id=workspace.id,
            user_id=admin_user.id,
            name="Aura",
            description="Friendly virtual personality for interview practice and feedback.",
        )
        db.add(persona)
        db.commit()

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

    conversation = db.query(Conversation).filter(Conversation.id == 1).first()
    if not conversation:
        conversation = Conversation(
            id=1,
            workspace_id=workspace.id,
            user_id=admin_user.id,
            persona_id=persona.id,
            title="Demo Conversation",
        )
        db.add(conversation)
        db.commit()

    logger.info("Demo data ready: workspace=1 role=1 user=1 persona=1 conversation=1")
