from models.role import Role
from models.user import User
from models.workspace import Workspace
from security.auth_security import hash_password


def test_register_returns_client_role(client, db_session):
    db_session.add_all(
        [
            Role(id=1, name="employee"),
            Role(id=2, name="admin"),
            Role(id=3, name="client"),
        ]
    )
    db_session.commit()

    response = client.post(
        "/auth/register",
        json={
            "full_name": "Client User",
            "email": "client@example.com",
            "password": "secret123",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["access_token"]
    assert body["user"]["role"] == "client"
    assert body["user"]["role_id"] == 3


def test_login_and_me_work(client, db_session):
    workspace = Workspace(name="Main Workspace")
    role = Role(id=3, name="client")
    db_session.add_all([workspace, role])
    db_session.commit()

    user = User(
        full_name="Client User",
        workspace_id=workspace.id,
        role_id=role.id,
        username="client-user",
        email="client@example.com",
        hashed_password=hash_password("secret123"),
    )
    db_session.add(user)
    db_session.commit()

    login_response = client.post(
        "/auth/login",
        json={"email": "client@example.com", "password": "secret123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "client@example.com"

