from models.notification import Notification
from models.role import Role
from models.user import User
from models.workspace import Workspace
from security.auth_security import hash_password


def _create_user(db_session, workspace_id: int, role_id: int, username: str, email: str) -> User:
    user = User(
        full_name=username,
        workspace_id=workspace_id,
        role_id=role_id,
        username=username,
        email=email,
        hashed_password=hash_password("secret123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _login(client, email: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": "secret123"})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_notifications_list_only_own(client, db_session):
    workspace = Workspace(name="Main Workspace")
    role = Role(id=1, name="employee")
    db_session.add_all([workspace, role])
    db_session.commit()

    u1 = _create_user(db_session, workspace.id, role.id, "u1", "u1@example.com")
    u2 = _create_user(db_session, workspace.id, role.id, "u2", "u2@example.com")

    db_session.add_all(
        [
            Notification(user_id=u1.id, title="A", content="A", is_read=False),
            Notification(user_id=u2.id, title="B", content="B", is_read=False),
        ]
    )
    db_session.commit()

    token = _login(client, "u1@example.com")
    response = client.get("/notifications", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["user_id"] == u1.id

