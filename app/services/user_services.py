from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_password, hash_password
from app.services.sms_service import send_otp
from app.core.logger import log_calls, get_logger
from app.services.otp import generate_numeric_otp, save_otp, get_otp, delete_otp
from sqlalchemy import select
from app.models import User
from fastapi import HTTPException, status

logger = get_logger(__name__)


@log_calls
async def get_me_user(user: User):
    return user


@log_calls
async def change_my_password(current_password: str, new_password: str, user: User, db: AsyncSession):

    if not verify_password(current_password, user.hashed_password):
        logger.warning(
            "BUSINESS invalid_current_password user_id=%s",
            user.id,
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong current password")

    user.hashed_password = hash_password(new_password)

    await db.commit()
    await db.refresh(user)

    logger.info(
        "BUSINESS password_changed user_id=%s",
        user.id,
    )

    return {
        "message": "Password updated successfully"
    }


@log_calls
async def forgot_my_password(phone_number: str, db: AsyncSession):

    result = await db.execute(
        select(User).where(User.phone_number == phone_number)
    )

    user = result.scalar_one_or_none()

    if not user:
        logger.warning(
            "BUSINESS phone_number_not_found phone_number=%s",
            phone_number,
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phone number not found")

    otp = generate_numeric_otp()

    await save_otp(phone_number, otp)

    send_otp(phone_number, otp)

    logger.info(
        "BUSINESS password_reset_otp_sent user_id=%s",
        user.id,
    )

    return {
        "message": "OTP sent successfully."
    }

@log_calls
async def reset_my_password(phone_number: str, otp: str, new_password: str, db: AsyncSession):

    result = await db.execute(
        select(User).where(User.phone_number == phone_number)
    )

    user = result.scalar_one_or_none()

    if not user:
        logger.warning(
            "BUSINESS phone_number_not_found phone_number=%s",
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phone number not found")

    saved_otp = await get_otp(phone_number)

    if saved_otp is None:
        logger.warning(
            "BUSINESS otp_expired phone_number=%s",
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired")

    if saved_otp != otp:
        logger.warning(
            "BUSINESS invalid_otp phone_number=%s",
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")

    user.hashed_password = hash_password(new_password)

    await db.commit()

    await delete_otp(phone_number)

    logger.info(
        "BUSINESS password_reset user_id=%s",
        user.id,
    )

    return {
        "message": "Password reset successfully."
    }

