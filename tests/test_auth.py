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
    assert body["token"]
    assert body["token_type"] == "bearer"
    assert body["user"]["name"] == "admin"
    assert body["user"]["email"] == "admin@example.com"
    assert body["user"]["role"] == "employee"
    assert "hashed_password" not in body["user"]

    user = db_session.query(User).filter(User.email == "admin@example.com").first()
    assert user is not None
    assert user.role.name == "employee"
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


def test_admin_can_list_users(client, db_session):
    workspace = Workspace(name="Main Workspace")
    admin_role = Role(name="admin")
    user_role = Role(name="employee")
    db_session.add_all([workspace, admin_role, user_role])
    db_session.commit()

    admin = User(
        full_name="Admin User",
        workspace_id=workspace.id,
        role_id=admin_role.id,
        username="admin-list",
        email="admin@dps.com",
        hashed_password=hash_password("secret123"),
    )
    normal_user = User(
        full_name="Normal User",
        workspace_id=workspace.id,
        role_id=user_role.id,
        username="normal-list",
        email="normal-list@example.com",
        hashed_password=hash_password("secret123"),
    )
    db_session.add_all([admin, normal_user])
    db_session.commit()

    login_response = client.post(
        "/auth/login",
        json={"email": "admin@dps.com", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_user_cannot_list_or_read_other_users(client, db_session):
    workspace = Workspace(name="Main Workspace")
    user_role = Role(name="employee")
    db_session.add_all([workspace, user_role])
    db_session.commit()

    user_one = User(
        full_name="User One",
        workspace_id=workspace.id,
        role_id=user_role.id,
        username="user-one-auth",
        email="one-auth@example.com",
        hashed_password=hash_password("secret123"),
    )
    user_two = User(
        full_name="User Two",
        workspace_id=workspace.id,
        role_id=user_role.id,
        username="user-two-auth",
        email="two-auth@example.com",
        hashed_password=hash_password("secret123"),
    )
    db_session.add_all([user_one, user_two])
    db_session.commit()
    db_session.refresh(user_two)

    login_response = client.post(
        "/auth/login",
        json={"email": "one-auth@example.com", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    list_response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {token}"},
    )
    other_user_response = client.get(
        f"/users/{user_two.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert list_response.status_code == 403
    assert other_user_response.status_code == 403


def test_cannot_create_second_admin(client, db_session):
    workspace = Workspace(name="Main Workspace")
    admin_role = Role(name="admin")
    db_session.add_all([workspace, admin_role])
    db_session.commit()

    existing_admin = User(
        full_name="Existing Admin",
        workspace_id=workspace.id,
        role_id=admin_role.id,
        username="existing-admin",
        email="admin@dps.com",
        hashed_password=hash_password("secret123"),
    )
    db_session.add(existing_admin)
    db_session.commit()

    login_response = client.post(
        "/auth/login",
        json={"email": "admin@dps.com", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "full_name": "Second Admin",
            "username": "second-admin",
            "email": "second-admin@example.com",
            "password": "secret123",
            "workspace_id": workspace.id,
            "role_id": admin_role.id,
        },
    )

    assert response.status_code == 400


def test_non_default_admin_is_demoted_on_login(client, db_session):
    workspace = Workspace(name="Main Workspace")
    admin_role = Role(name="admin")
    employee_role = Role(name="employee")
    db_session.add_all([workspace, admin_role, employee_role])
    db_session.commit()

    accidental_admin = User(
        full_name="Accidental Admin",
        workspace_id=workspace.id,
        role_id=admin_role.id,
        username="accidental-admin",
        email="accidental@example.com",
        hashed_password=hash_password("secret123"),
    )
    db_session.add(accidental_admin)
    db_session.commit()

    response = client.post(
        "/auth/login",
        json={"email": "accidental@example.com", "password": "secret123"},
    )

    assert response.status_code == 200
    assert response.json()["user"]["role"] == "employee"

    db_session.refresh(accidental_admin)
    assert accidental_admin.role_id == employee_role.id
