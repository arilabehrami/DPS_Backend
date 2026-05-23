from models.role import Role
from models.user import User
from models.workspace import Workspace
from security.auth_security import hash_password, verify_password


def seed_workspace_and_role(db_session, role_name="admin"):
    workspace = Workspace(name="Main Workspace")
    role = Role(name=role_name)
    db_session.add_all([workspace, role])
    db_session.commit()
    db_session.refresh(workspace)
    db_session.refresh(role)
    return workspace, role


def test_register_hashes_password_and_returns_token(client, db_session):
    workspace, role = seed_workspace_and_role(db_session)

    response = client.post(
        "/auth/register",
        json={
            "workspace_id": workspace.id,
            "role_id": role.id,
            "username": "admin",
            "email": "admin@example.com",
            "password": "secret123",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "admin@example.com"
    assert "hashed_password" not in body["user"]

    user = db_session.query(User).filter(User.email == "admin@example.com").first()
    assert user is not None
    assert user.hashed_password != "secret123"
    assert verify_password("secret123", user.hashed_password)


def test_login_rejects_wrong_password(client, db_session):
    workspace, role = seed_workspace_and_role(db_session)
    user = User(
        workspace_id=workspace.id,
        role_id=role.id,
        username="admin",
        email="admin@example.com",
        hashed_password=hash_password("secret123"),
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_admin_check_requires_admin_role(client, db_session):
    workspace, role = seed_workspace_and_role(db_session, role_name="user")
    user = User(
        workspace_id=workspace.id,
        role_id=role.id,
        username="normal-user",
        email="user@example.com",
        hashed_password=hash_password("secret123"),
    )
    db_session.add(user)
    db_session.commit()

    login_response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/admin-check",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
