from models.role import Role
from models.user import User
from models.workspace import Workspace
from security.auth_security import hash_password


def test_admin_create_user_forces_employee_role_id_one(client, db_session):
    workspace = Workspace(name="Main Workspace")
    roles = [
        Role(id=1, name="employee"),
        Role(id=2, name="admin"),
        Role(id=3, name="client"),
    ]
    db_session.add(workspace)
    db_session.add_all(roles)
    db_session.commit()

    admin_user = User(
        full_name="Admin",
        workspace_id=workspace.id,
        role_id=2,
        username="admin",
        email="admin@example.com",
        hashed_password=hash_password("secret123"),
    )
    db_session.add(admin_user)
    db_session.commit()

    login_response = client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    create_response = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "full_name": "Created User",
            "username": "created-user",
            "email": "created@example.com",
            "password": "secret123",
            "workspace_id": workspace.id,
            "role_id": 3,
        },
    )

    assert create_response.status_code == 200
    assert create_response.json()["role_id"] == 1

