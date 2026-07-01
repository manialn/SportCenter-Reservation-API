from pydantic import BaseModel, Field, field_validator
import re

class UserRegister(BaseModel):
    username: str = Field(..., min_length=4, max_length=125,
    description="Username must be 4-125 characters, containing only letters, numbers, underscores, dots, or hyphens.")

    phone_number: str = Field(..., min_length=11, max_length=11,
    description="Iranian mobile phone number starting with 09 followed by 9 digits.")

    password: str = Field(..., min_length=6,
    description="Password must be at least 6 characters long and may contain special characters.")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        v = v.strip()
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", v):
            raise ValueError("Invalid username")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        v = v.strip()
        if not re.fullmatch(r"[A-Za-z0-9_.!@#$%^&*-]+", v):
            raise ValueError("Invalid password")
        return v

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v):
        v = v.strip()
        if not re.fullmatch(r"09\d{9}", v):
            raise ValueError("Invalid phone number")
        return v

class Token(BaseModel):
    access_token : str
    token_type : str
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str