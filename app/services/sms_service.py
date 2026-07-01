from app.core.logger import get_logger

logger = get_logger(__name__)

def send_otp(phone_number: str, otp: str):
    logger.info("OTP generated phone_number=%s", phone_number)
    print(f"[OTP] Phone: {phone_number} | Code: {otp}")



# call sms provider