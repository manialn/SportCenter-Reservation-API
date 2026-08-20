from app.core.dependency import db_dependency,user_dependency
from fastapi import APIRouter,status,Depends
from app.schemas.user import UserOut,UserVerification,ForgotPasswordRequest,ResetPasswordRequest
from app.schemas.error import ErrorResponse
from app.services.user_service import get_me_user,change_my_password,forgot_my_password,reset_my_password
from app.limiter.rate_limiter import RedisRateLimiter

router = APIRouter(
    prefix="/users"
)

@router.get("/me",status_code=status.HTTP_200_OK,response_model=UserOut)
async def get_me(user: user_dependency):
    return await get_me_user(user)

@router.patch("/change_password",status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Wrong current password"},
    },)
async def change_password(request: UserVerification,user: user_dependency,db: db_dependency):
    return await change_my_password(request.current_password,request.new_password,user,db)

@router.post("/forgot-password", status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Phone number not found"},
        429: {"model": ErrorResponse, "description": "Too many password reset requests"},
    },)
async def forgot_password(request: ForgotPasswordRequest,db: db_dependency, _: None = Depends(
        RedisRateLimiter(
            limit=3,
            window=600,
            key_prefix="forgot_password",
        )
    ),):
    return await forgot_my_password(request.phone_number,db)

@router.patch("/reset-password", status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "OTP is invalid or expired"},
        404: {"model": ErrorResponse, "description": "Phone number not found"},
        429: {"model": ErrorResponse, "description": "Too many password reset requests"},
    },)
async def reset_password(request: ResetPasswordRequest, db: db_dependency, _: None = Depends(
        RedisRateLimiter(
            limit=3,
            window=600,
            key_prefix="reset_password",
        )
    ),):
    return await reset_my_password(request.phone_number, request.otp, request.new_password, db)

