from app.core.dependency import db_dependency,form_data
from fastapi import APIRouter,status,Depends
from app.schemas.auth import UserRegister,Token,RefreshTokenResponse,RefreshTokenRequest
from app.services.auth_service import register_user,login_user,refresh_access_token,logout_user
from app.schemas.error import ErrorResponse
from app.limiter.rate_limiter import RedisRateLimiter


router = APIRouter(
    prefix="/auth"
)

@router.post("/register",status_code=status.HTTP_201_CREATED,
responses={
        400: {"model": ErrorResponse,"description": "Username or phone number already exists",},
        429: {"model": ErrorResponse,"description": "Too many registration requests",},
    },)
async def register(request: UserRegister,db: db_dependency, _: None = Depends(
        RedisRateLimiter(
            limit=5,
            window=60,
            key_prefix="register",
        )
    ),):
    return await register_user(request.username,request.phone_number,request.password, db)

@router.post("/login", status_code=status.HTTP_200_OK,response_model=Token,
    responses={
        401: {"model": ErrorResponse,"description": "Invalid credentials",},
        429: {"model": ErrorResponse,"description": "Too many login requests",},
    },)
async def login(form_data: form_data, db: db_dependency, _: None = Depends(
        RedisRateLimiter(
            limit=5,
            window=60,
            key_prefix="login",
        )
    ),):
    return await login_user(form_data, db)

@router.post('/refresh',status_code=status.HTTP_200_OK,response_model=RefreshTokenResponse,
    responses={
        401: {"model": ErrorResponse,"description": "Invalid, expired, revoked, or otherwise unusable refresh token",},
        404: {"model": ErrorResponse,"description": "User not found",},
    },)
async def refresh(request: RefreshTokenRequest,db: db_dependency):
    return await refresh_access_token(request.refresh_token, db)

@router.post("/logout",status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse,"description": "Invalid, expired, or already revoked refresh token",},
    },)
async def logout(request: RefreshTokenRequest,db: db_dependency):
    return await logout_user(request.refresh_token,db)