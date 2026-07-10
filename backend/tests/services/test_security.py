import uuid
import pytest
from datetime import datetime, timedelta, timezone
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)


def test_password_hash_and_verify():
    password = "TestPassword123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)


def test_create_access_token():
    user_id = str(uuid.uuid4())
    token = create_access_token(user_id)
    decoded = decode_token(token)
    assert decoded["sub"] == user_id
    assert decoded["type"] == "access"
    assert "exp" in decoded


def test_create_refresh_token():
    user_id = str(uuid.uuid4())
    token = create_refresh_token(user_id)
    decoded = decode_token(token)
    assert decoded["sub"] == user_id
    assert decoded["type"] == "refresh"
    assert "exp" in decoded


def test_create_token_with_custom_expiry():
    user_id = str(uuid.uuid4())
    delta = timedelta(minutes=30)
    token = create_access_token(user_id, expires_delta=delta)
    decoded = decode_token(token)
    assert decoded["sub"] == user_id


def test_decode_invalid_token():
    with pytest.raises(ValueError, match="Invalid token"):
        decode_token("not.a.valid.token")


def test_decode_expired_token():
    user_id = str(uuid.uuid4())
    token = create_access_token(user_id, expires_delta=timedelta(seconds=-1))
    with pytest.raises(ValueError, match="Token has expired"):
        decode_token(token)
