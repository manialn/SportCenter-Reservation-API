from app.core.dependency import db_dependency,form_data,get_current_access
from fastapi import APIRouter,status,Depends
from app.schemas.auth import UserRegister,Token,RefreshTokenResponse,RefreshTokenRequest
from app.services.auth_service import register_user,login_user,refresh_access_token,logout_user


router = APIRouter(
    prefix="/auth"
)

@router.post("/register",status_code=status.HTTP_201_CREATED)
async def register(request: UserRegister,db: db_dependency):
    return await register_user(request.username,request.phone_number,request.password, db)

@router.post("/login", status_code=status.HTTP_200_OK, response_model=Token)
async def login(form_data: form_data, db: db_dependency):
    return await login_user(form_data, db)

@router.post('/refresh',status_code=status.HTTP_200_OK, response_model=RefreshTokenResponse)
async def refresh(request: RefreshTokenRequest,db: db_dependency):
    return await refresh_access_token(request.refresh_token, db)

@router.post("/logout",status_code=status.HTTP_200_OK)
async def logout(current_user = Depends(get_current_access)):
    return await logout_user()