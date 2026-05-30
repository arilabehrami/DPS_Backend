import pytest
from jose import jwt

from security import auth_security


@pytest.mark.no_db
def test_hash_and_verify_password():
    hashed = auth_security.hash_password("secret123")
    assert hashed != "secret123"
    assert auth_security.verify_password("secret123", hashed) is True
    assert auth_security.verify_password("wrong", hashed) is False


@pytest.mark.no_db
def test_create_access_token_contains_subject():
    token = auth_security.create_access_token({"sub": "user@example.com"})
    payload = jwt.decode(token, auth_security.SECRET_KEY, algorithms=[auth_security.ALGORITHM])
    assert payload.get("sub") == "user@example.com"
    assert "exp" in payload

