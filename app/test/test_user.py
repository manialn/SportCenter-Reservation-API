import pytest
from fastapi import status
from app.core.security import verify_password
from app.core.redis_client import get_redis



@pytest.mark.asyncio
async def test_get_me_success(authorized_client, test_user):

    response = await authorized_client.get("/users/me")
    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert body["username"] == test_user.username
    assert body["phone_number"] == test_user.phone_number
    assert body["role"] == test_user.role.value
    assert body["is_phone_verified"] == test_user.is_phone_verified
    assert body["created_at"] is not None

@pytest.mark.asyncio
async def test_get_me_without_access_token(client):

    response = await client.get("/users/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

#change_password
@pytest.mark.asyncio
async def test_change_password_success(authorized_client, test_user, db_session):

    response = await authorized_client.patch(
        "/users/change_password",
        json={"current_password": "12345678", "new_password": "newpassword123"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Password updated successfully"}

    await db_session.refresh(test_user)
    assert verify_password("newpassword123", test_user.hashed_password)

@pytest.mark.asyncio
async def test_change_password_with_wrong_current_password(authorized_client):

    response = await authorized_client.patch(
        "/users/change_password",
        json={"current_password": "wrongpassword", "new_password": "newpassword123"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Wrong current password"}

@pytest.mark.asyncio
async def test_change_password_without_access_token(client):

    response = await client.patch(
        "/users/change_password",
        json={"current_password": "12345678", "new_password": "newpassword123"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

#forgot_password
@pytest.mark.asyncio
async def test_forgot_password_success(client, test_user):

    response = await client.post(
        "/users/forgot-password",
        json={"phone_number": test_user.phone_number},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "OTP sent successfully."}

@pytest.mark.asyncio
async def test_forgot_password_phone_not_found(client):

    response = await client.post(
        "/users/forgot-password",
        json={"phone_number": "09999999999"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Phone number not found"}

@pytest.mark.asyncio
async def test_forgot_password_without_phone_number(client):

    response = await client.post(
        "/users/forgot-password",
        json={},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

#reset_password
@pytest.mark.asyncio
async def test_reset_password_success(client, test_user, db_session):

    redis = get_redis()
    await redis.set(f"otp:{test_user.phone_number}","123456",ex=120)


    response = await client.patch(
        "/users/reset-password",
        json={
            "phone_number": test_user.phone_number,
            "otp": "123456",
            "new_password": "newpassword123",
        },
    )
    print(response.status_code)
    print(response.text)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Password reset successfully."}

    await db_session.refresh(test_user)

    assert verify_password("newpassword123", test_user.hashed_password)

@pytest.mark.asyncio
async def test_reset_password_phone_not_found(client):

    response = await client.patch(
        "/users/reset-password",
        json={
            "phone_number": "09999999999",
            "otp": "123456",
            "new_password": "newpassword123",
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Phone number not found"}

@pytest.mark.asyncio
async def test_reset_password_expired_otp(client, test_user):

    response = await client.patch(
        "/users/reset-password",
        json={
            "phone_number": test_user.phone_number,
            "otp": "123456",
            "new_password": "newpassword123",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "OTP has expired"}

@pytest.mark.asyncio
async def test_reset_password_invalid_otp(client, test_user):

    redis = get_redis()
    await redis.set(f"otp:{test_user.phone_number}","654321",ex=120)



    response = await client.patch(
        "/users/reset-password",
        json={
            "phone_number": test_user.phone_number,
            "otp": "123456",
            "new_password": "newpassword123",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Invalid OTP"}

@pytest.mark.asyncio
async def test_reset_password_validation_error(client):

    response = await client.patch(
        "/users/reset-password",
        json={},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY