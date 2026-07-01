from pydantic import BaseModel,ConfigDict,Field
from datetime import datetime
from app.enumsfile.enum import UserRole

class UserOut(BaseModel):
    username: str
    phone_number: str
    role : UserRole
    is_phone_verified: bool
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

class UserVerification(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6)

class ForgotPasswordRequest(BaseModel):
    phone_number: str

class ResetPasswordRequest(BaseModel):
    phone_number: str
    otp: str
    new_password: str