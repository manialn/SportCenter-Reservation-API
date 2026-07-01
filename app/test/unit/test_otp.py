from app.services.otp import generate_numeric_otp
from app.core.config import settings


def test_generate_numeric_otp_length():

    otp = generate_numeric_otp()

    assert len(otp) == settings.OTP_LENGTH


def test_generate_numeric_otp_is_numeric():

    otp = generate_numeric_otp()

    assert otp.isdigit()