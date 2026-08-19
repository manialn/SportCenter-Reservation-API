import pytest
from datetime import timedelta
from fastapi import status,HTTPException
from uuid import uuid4
from jose import jwt
from app.core.config import settings
from app.core.token import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)


def test_create_access_token():
    user_id = uuid4()

    token = create_access_token(
        user_id,
        timedelta(minutes=30),
    )

    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    assert payload["sub"] == str(user_id)
    assert payload["type"] == "access"
    assert "exp" in payload

def test_create_refresh_token():
    user_id = uuid4()

    token, jti, expires_at = create_refresh_token(
        user_id,
        timedelta(days=7),
    )

    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    assert payload["sub"] == str(user_id)
    assert payload["type"] == "refresh"
    assert payload["jti"] == str(jti)
    assert "exp" in payload
    assert expires_at is not None

def test_verify_refresh_token():
    user_id = uuid4()

    token, jti, expires_at = create_refresh_token(
        user_id,
        timedelta(days=7),
    )

    verified_user_id, verified_jti, verified_expires_at = verify_refresh_token(
        token
    )

    assert verified_user_id == user_id
    assert verified_jti == jti
    assert abs(
        (verified_expires_at - expires_at).total_seconds()
    ) < 1

def test_verify_access_token_as_refresh_token():
    user_id = uuid4()

    token = create_access_token(
        user_id,
        timedelta(minutes=30),
    )

    with pytest.raises(HTTPException) as exc_info:
        verify_refresh_token(token)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid token type"