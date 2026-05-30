import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

import middleware.authentication_middleware as auth_mw
from middleware.authentication_middleware import AuthenticationMiddleware


class _FakeQuery:
    def __init__(self, user):
        self._user = user

    def options(self, *_args, **_kwargs):
        return self

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return self._user


class _FakeSession:
    def __init__(self, user):
        self._user = user

    def query(self, *_args, **_kwargs):
        return _FakeQuery(self._user)

    def close(self):
        return None


@pytest.mark.no_db
def test_authentication_middleware_sets_current_user(monkeypatch):
    fake_user = type("UserObj", (), {"id": 10, "email": "u@example.com"})()

    monkeypatch.setattr(
        auth_mw.jwt,
        "decode",
        lambda token, *_args, **_kwargs: {"sub": "10"} if token == "valid-token" else {},
    )
    monkeypatch.setattr(auth_mw, "SessionLocal", lambda: _FakeSession(fake_user))

    app = FastAPI()
    app.add_middleware(AuthenticationMiddleware)

    @app.get("/whoami")
    def whoami(request: Request):
        current_user = getattr(request.state, "current_user", None)
        return {"user_id": current_user.id if current_user else None}

    client = TestClient(app)

    no_token = client.get("/whoami")
    assert no_token.status_code == 200
    assert no_token.json() == {"user_id": None}

    with_token = client.get("/whoami", headers={"Authorization": "Bearer valid-token"})
    assert with_token.status_code == 200
    assert with_token.json() == {"user_id": 10}

