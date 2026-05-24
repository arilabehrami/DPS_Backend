from database import Base, engine, SessionLocal
import models
from models.persona import Persona
from models.personality import Personality
from models.role import Role
from models.user import User
from models.workspace import Workspace
from services.user import hash_password


Base.metadata.create_all(bind=engine)


def get_or_create(db, model, defaults=None, **filters):
    obj = db.query(model).filter_by(**filters).first()
    if obj:
        return obj

    payload = {**filters, **(defaults or {})}
    obj = model(**payload)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def run_seed():
    db = SessionLocal()

    try:
        workspace = get_or_create(db, Workspace, name="Default Workspace")
        admin_role = get_or_create(db, Role, name="admin")
        user_role = get_or_create(db, Role, name="user")

        admin = db.query(User).filter(User.email == "admin@dps.com").first()
        if not admin:
            admin = User(
                full_name="Admin User",
                username="admin",
                email="admin@dps.com",
                hashed_password=hash_password("admin123"),
                workspace_id=workspace.id,
                role_id=admin_role.id,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
        else:
            admin.full_name = admin.full_name or "Admin User"
            admin.username = admin.username or "admin"
            admin.workspace_id = workspace.id
            admin.role_id = admin_role.id
            db.commit()
            db.refresh(admin)

        demo_user = db.query(User).filter(User.email == "user@dps.com").first()
        if not demo_user:
            demo_user = User(
                full_name="Demo User",
                username="demo-user",
                email="user@dps.com",
                hashed_password=hash_password("user123"),
                workspace_id=workspace.id,
                role_id=user_role.id,
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
        else:
            demo_user.full_name = demo_user.full_name or "Demo User"
            demo_user.username = demo_user.username or "demo-user"
            demo_user.workspace_id = workspace.id
            demo_user.role_id = user_role.id
            db.commit()
            db.refresh(demo_user)

        extra_admins = (
            db.query(User)
            .filter(User.email != "admin@dps.com", User.role_id == admin_role.id)
            .all()
        )
        for user in extra_admins:
            user.role_id = user_role.id
        if extra_admins:
            db.commit()

        aura = get_or_create(
            db,
            Persona,
            defaults={
                "description": "Helpful AI assistant for the Digital Personality Simulator.",
                "workspace_id": workspace.id,
                "user_id": admin.id,
            },
            name="Aura",
        )
        aura.workspace_id = workspace.id
        aura.user_id = aura.user_id or admin.id

        personality = db.query(Personality).filter(
            Personality.persona_id == aura.id,
            Personality.name == "Aura",
        ).first()
        if not personality:
            personality = Personality(
                persona_id=aura.id,
                user_id=admin.id,
                workspace_id=workspace.id,
                name="Aura",
                description=aura.description,
            )
            db.add(personality)
        else:
            personality.user_id = personality.user_id or admin.id
            personality.workspace_id = workspace.id
            personality.description = personality.description or aura.description

        db.commit()

        print("Seed completed successfully.")
        print("--------------------------------")
        print(f"Workspace: {workspace.name}")
        print(f"Workspace ID: {workspace.id}")
        print("Admin email: admin@dps.com")
        print("Admin password: admin123")
        print("User email: user@dps.com")
        print("User password: user123")
        print(f"Aura Persona ID: {aura.id}")
        print(f"Aura Personality ID: {personality.id}")
        print("--------------------------------")

    except Exception as exc:
        db.rollback()
        print("Seed failed.")
        print(str(exc))
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
