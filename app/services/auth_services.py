from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from app.models import User
from app.core.security import hash_password, verify_password
from app.core.token import create_access_token, create_refresh_token, verify_refresh_token
from app.core.config import settings
from app.core.logger import log_calls, get_logger

logger = get_logger(__name__)


@log_calls
async def register_user(username: str, phone_number: str, password: str, db: AsyncSession):

    result = await db.execute(
        select(User).where(
            (User.username == username) |
            (User.phone_number == phone_number)
        )
    )

    user_exist = result.scalar_one_or_none()

    if user_exist:
        logger.warning("Register failed user already exists username=%s", username)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or phonenumber already exists")

    create_user = User(
        username=username,
        phone_number=phone_number,
        hashed_password=hash_password(password)
    )

    try:
        db.add(create_user)
        await db.commit()
        await db.refresh(create_user)
        logger.info("User registered successfully user_id=%s username=%s", create_user.id, create_user.username)
    except Exception:
        await db.rollback()
        logger.error("Register transaction failed username=%s", username)
        raise

    return {"message": "User created successfully"}


@log_calls
async def authentication_user(identifier: str, password: str, db: AsyncSession):
    logger.info("Authentication attempt")

    result = await db.execute(
        select(User).where(
            (User.username == identifier) |
            (User.phone_number == identifier)
        )
    )

    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        logger.warning("Authentication failed")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    logger.info("Authentication successful user_id=%s", user.id)

    return user


@log_calls
async def login_user(form_data: OAuth2PasswordRequestForm, db: AsyncSession):

    user = await authentication_user(form_data.username, form_data.password, db)

    token = create_access_token(user.id, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_refresh_token(user.id, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))

    logger.info("Login successful user_id=%s", user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }


@log_calls
async def refresh_access_token(refresh_token: str, db: AsyncSession):
    logger.info("Refresh token request")

    user_id = verify_refresh_token(refresh_token)

    result = await db.execute(
        select(User).where(
            User.id == user_id
        )
    )

    user = result.scalar_one_or_none()

    if not user:
        logger.warning("Refresh token failed user not found user_id=%s", user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_access_token = create_access_token(user.id, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

    logger.info("Access token refreshed user_id=%s", user.id)

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@log_calls
async def logout_user():
    logger.info("User logout")
    return {"message": "Logged out successfully"}
