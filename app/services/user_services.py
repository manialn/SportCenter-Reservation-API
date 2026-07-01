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
    logger.info("Get current user user_id=%s username=%s", user.id, user.username)
    return user


@log_calls
async def change_my_password(current_password: str, new_password: str, user: User, db: AsyncSession):
    logger.info("Password change attempt user_id=%s username=%s", user.id, user.username)

    if not verify_password(current_password, user.hashed_password):
        logger.warning("Password change failed wrong current password user_id=%s", user.id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong current password")

    user.hashed_password = hash_password(new_password)

    await db.commit()
    await db.refresh(user)

    logger.info("Password changed successfully user_id=%s", user.id)

    return {
        "message": "Password updated successfully"
    }


@log_calls
async def forgot_my_password(phone_number: str, db: AsyncSession):
    logger.info("Forgot password requested phone_number=%s", phone_number)

    result = await db.execute(
        select(User).where(User.phone_number == phone_number)
    )

    user = result.scalar_one_or_none()

    if not user:
        logger.warning("Forgot password failed phone number not found phone_number=%s", phone_number)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phone number not found")

    otp = generate_numeric_otp()

    await save_otp(phone_number, otp)

    logger.info("OTP generated and saved user_id=%s phone_number=%s", user.id, phone_number)

    send_otp(phone_number, otp)

    logger.info("OTP sent successfully user_id=%s phone_number=%s", user.id, phone_number)

    return {
        "message": "OTP sent successfully."
    }


@log_calls
async def reset_my_password(phone_number: str, otp: str, new_password: str, db: AsyncSession):
    logger.info("Password reset attempt phone_number=%s", phone_number)

    result = await db.execute(
        select(User).where(User.phone_number == phone_number)
    )

    user = result.scalar_one_or_none()

    if not user:
        logger.warning("Password reset failed phone number not found phone_number=%s", phone_number)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phone number not found")

    saved_otp = await get_otp(phone_number)

    if saved_otp is None:
        logger.warning("Password reset failed OTP expired phone_number=%s", phone_number)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired")

    if saved_otp != otp:
        logger.warning("Password reset failed invalid OTP phone_number=%s", phone_number)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")

    user.hashed_password = hash_password(new_password)

    await db.commit()

    logger.info("Password reset successfully user_id=%s", user.id)

    await delete_otp(phone_number)

    logger.info("OTP deleted after successful password reset user_id=%s", user.id)

    return {
        "message": "Password reset successfully."
    }

