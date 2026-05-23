from models.persona import Persona
from models.role import Role
from models.user import User
from models.workspace import Workspace
from security.auth_security import hash_password


def seed_two_tenants(db_session):
    admin_role = Role(name="admin")
    workspace_one = Workspace(name="Workspace One")
    workspace_two = Workspace(name="Workspace Two")
    db_session.add_all([admin_role, workspace_one, workspace_two])
    db_session.commit()

    user_one = User(
        workspace_id=workspace_one.id,
        role_id=admin_role.id,
        username="user-one",
        email="one@example.com",
        hashed_password=hash_password("secret123"),
    )
    user_two = User(
        workspace_id=workspace_two.id,
        role_id=admin_role.id,
        username="user-two",
        email="two@example.com",
        hashed_password=hash_password("secret123"),
    )
    db_session.add_all([user_one, user_two])
    db_session.commit()
    db_session.refresh(user_one)
    db_session.refresh(user_two)

    persona_one = Persona(
        workspace_id=workspace_one.id,
        user_id=user_one.id,
        name="Own Persona",
        description="Visible persona",
    )
    persona_two = Persona(
        workspace_id=workspace_two.id,
        user_id=user_two.id,
        name="Other Persona",
        description="Hidden persona",
    )
    db_session.add_all([persona_one, persona_two])
    db_session.commit()
    db_session.refresh(persona_one)
    db_session.refresh(persona_two)

    return workspace_one, workspace_two, user_one, user_two, persona_one, persona_two


def login(client, email):
    response = client.post(
        "/auth/login",
        json={"email": email, "password": "secret123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_list_personas_returns_only_current_workspace(client, db_session):
    _, _, _, _, persona_one, _ = seed_two_tenants(db_session)
    token = login(client, "one@example.com")

    response = client.get(
        "/personas/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    personas = response.json()
    assert len(personas) == 1
    assert personas[0]["id"] == persona_one.id
    assert personas[0]["name"] == "Own Persona"


def test_cannot_read_persona_from_another_workspace(client, db_session):
    _, _, _, _, _, persona_two = seed_two_tenants(db_session)
    token = login(client, "one@example.com")

    response = client.get(
        f"/personas/{persona_two.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_cannot_create_persona_in_another_workspace(client, db_session):
    _, workspace_two, user_one, _, _, _ = seed_two_tenants(db_session)
    token = login(client, "one@example.com")

    response = client.post(
        "/personas/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "workspace_id": workspace_two.id,
            "user_id": user_one.id,
            "name": "Invalid Persona",
            "description": "Should be rejected",
        },
    )

    assert response.status_code == 403
