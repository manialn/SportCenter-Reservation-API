import secrets

from app.core.config import settings
from app.core.redis_client import get_redis
from app.core.logger import log_calls, get_logger

logger = get_logger(__name__)


@log_calls
def generate_numeric_otp() -> str:
    otp = "".join(
        str(secrets.randbelow(10))
        for _ in range(settings.OTP_LENGTH)
    )

    return otp


def otp_key(phone_number: str) -> str:
    return f"otp:{phone_number}"


@log_calls
async def save_otp(phone_number: str, otp: str) -> None:
    logger.info("Saving OTP phone_number=%s", phone_number)

    redis = get_redis()

    await redis.set(
        otp_key(phone_number),
        otp,
        ex=settings.OTP_EXPIRE_SECONDS,
    )

    logger.info("OTP saved phone_number=%s", phone_number)


@log_calls
async def get_otp(phone_number: str) -> str | None:
    logger.info("Getting OTP phone_number=%s", phone_number)

    redis = get_redis()

    otp = await redis.get(
        otp_key(phone_number)
    )

    logger.info("OTP lookup result found=%s phone_number=%s", bool(otp), phone_number)

    return otp


@log_calls
async def delete_otp(phone_number: str) -> None:
    logger.info("Deleting OTP phone_number=%s", phone_number)

    redis = get_redis()

    await redis.delete(
        otp_key(phone_number)
    )

    logger.info("OTP deleted phone_number=%s", phone_number)
