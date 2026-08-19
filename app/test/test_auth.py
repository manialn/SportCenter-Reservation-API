from fastapi import status
import pytest

#register
@pytest.mark.asyncio
async def test_register_success(client):

    response = await client.post(
        "/auth/register",
        json={
            "username": "mani",
            "phone_number": "09123456789",
            "password": "12345678",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"message": "User created successfully"}

@pytest.mark.asyncio
async def test_register_duplicate_username(client, test_user):
    response = await client.post(
        "/auth/register",
        json={
            "username": test_user.username,
            "phone_number": "09123456789",
            "password": "12345678",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Username or phonenumber already exists"}


@pytest.mark.asyncio
async def test_register_duplicate_phone_number(client, test_user):

    response = await client.post(
        "/auth/register",
        json={
            "username": "another_user",
            "phone_number": test_user.phone_number,
            "password": "12345678",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Username or phonenumber already exists"}

#login
@pytest.mark.asyncio
async def test_successful_login_with_username(client, test_user):
    response = await client.post(
        "/auth/login",
        data={
            "username": test_user.username,
            "password": "12345678",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_successful_login_with_phone_number(client, test_user):
    response = await client.post(
        "/auth/login",
        data={
            "username": test_user.phone_number,
            "password": "12345678",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_with_wrong_password(client, test_user):
    response = await client.post(
        "/auth/login",
        data={
            "username": test_user.username,
            "password": "wrongpassword",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid credentials"}

@pytest.mark.asyncio
async def test_login_with_nonexistent_user(client):
    response = await client.post(
        "/auth/login",
        data={
            "username": "unknown_user",
            "password": "12345678",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid credentials"}

#refresh
@pytest.mark.asyncio
async def test_refresh_token_success(client, refresh_token):
    response = await client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"
    assert body["refresh_token"] != refresh_token

@pytest.mark.asyncio
async def test_refresh_token_rotation(client, refresh_token):
    response = await client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    new_refresh_token = response.json()["refresh_token"]

    response = await client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Refresh token has been revoked"

    response = await client.post(
        "/auth/refresh",
        json={
            "refresh_token": new_refresh_token,
        },
    )

    assert response.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_refresh_invalid_token(client):
    response = await client.post(
        "/auth/refresh",
        json={
            "refresh_token": "invalid_token",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Refresh token is invalid or expired"}

@pytest.mark.asyncio
async def test_refresh_with_access_token(client, access_token):
    response = await client.post(
        "/auth/refresh",
        json={
            "refresh_token": access_token,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid token type"

@pytest.mark.asyncio
async def test_logout_success(client, refresh_token):
    response = await client.post(
        "/auth/logout",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Logged out successfully"}

@pytest.mark.asyncio
async def test_logout_with_revoked_token(client, refresh_token):
    response = await client.post(
        "/auth/logout",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    response = await client.post(
        "/auth/logout",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Refresh token has already been revoked"}

@pytest.mark.asyncio
async def test_logout_with_invalid_token(client):
    response = await client.post(
        "/auth/logout",
        json={
            "refresh_token": "invalid_token",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Refresh token is invalid or expired"}

    