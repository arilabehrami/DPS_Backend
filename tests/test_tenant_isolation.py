from models.persona import Persona
from models.conversation import Conversation
from models.message import Message
from models.personality import Personality
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


def test_user_sees_only_own_conversations_and_messages(client, db_session):
    workspace = Workspace(name="Shared Workspace")
    admin_role = Role(name="admin")
    db_session.add_all([workspace, admin_role])
    db_session.commit()

    user_one = User(
        full_name="User One",
        workspace_id=workspace.id,
        role_id=admin_role.id,
        username="history-one",
        email="history-one@example.com",
        hashed_password=hash_password("secret123"),
    )
    user_two = User(
        full_name="User Two",
        workspace_id=workspace.id,
        role_id=admin_role.id,
        username="history-two",
        email="history-two@example.com",
        hashed_password=hash_password("secret123"),
    )
    db_session.add_all([user_one, user_two])
    db_session.commit()
    db_session.refresh(user_one)
    db_session.refresh(user_two)

    persona = Persona(
        workspace_id=workspace.id,
        user_id=user_one.id,
        name="Aura",
        description="Assistant",
    )
    db_session.add(persona)
    db_session.commit()
    db_session.refresh(persona)

    personality = Personality(
        persona_id=persona.id,
        user_id=user_one.id,
        workspace_id=workspace.id,
        name="Aura",
        description="Assistant",
    )
    db_session.add(personality)
    db_session.commit()
    db_session.refresh(personality)

    own_conversation = Conversation(
        user_id=user_one.id,
        personality_id=personality.id,
        workspace_id=workspace.id,
        title="Own chat",
    )
    other_conversation = Conversation(
        user_id=user_two.id,
        personality_id=personality.id,
        workspace_id=workspace.id,
        title="Other chat",
    )
    db_session.add_all([own_conversation, other_conversation])
    db_session.commit()
    db_session.refresh(own_conversation)
    db_session.refresh(other_conversation)

    own_message = Message(
        conversation_id=own_conversation.id,
        workspace_id=workspace.id,
        sender_type="user",
        sender_user_id=user_one.id,
        content="mine",
    )
    other_message = Message(
        conversation_id=other_conversation.id,
        workspace_id=workspace.id,
        sender_type="user",
        sender_user_id=user_two.id,
        content="not mine",
    )
    db_session.add_all([own_message, other_message])
    db_session.commit()

    token = login(client, "history-one@example.com")

    conversations_response = client.get(
        "/conversations/",
        headers={"Authorization": f"Bearer {token}"},
    )
    messages_response = client.get(
        "/messages/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert conversations_response.status_code == 200
    assert [item["id"] for item in conversations_response.json()] == [own_conversation.id]
    assert messages_response.status_code == 200
    assert [item["content"] for item in messages_response.json()] == ["mine"]
